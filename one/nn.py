"""
Date: 2 June 2020
Goal: 01 Neural network and training.
Author: Harsha HN harshahn@kth.se
"""
#%%---------------
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt 
import itertools

#Define the neural network
class neuralnet(nn.Module):
    def __init__(self, input_size, output_size, layers, dropout=0.1):
        super().__init__()
        
        # kernels
        self.bnorm = nn.BatchNorm1d(input_size)
        all_layers = []
        # inputsize = num_categorical_cols + num_numerical_cols
        for i in layers:
            all_layers.append(nn.Linear(input_size, i))
            all_layers.append(nn.ReLU(inplace=True))
            all_layers.append(nn.BatchNorm1d(i))
            #all_layers.append(nn.Dropout(dropout))
            input_size = i
        
        if len(layers) == 0: layers = [input_size]
        
        all_layers.extend([ nn.Linear(layers[-1], output_size),
                            nn.ReLU(inplace=True),
                            nn.BatchNorm1d(output_size)])
        self.layers = nn.Sequential(*all_layers)
        # initializations
        self.layers.apply(self._init_weights)

    def forward(self, x):
        x = self.bnorm(x)
        #x = torch.cat([x_categorical, x_numerical], 1)
        x = self.layers(x)
        return x
    
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight, gain=nn.init.calculate_gain('relu'))
            nn.init.constant_(m.bias, 0.0)

    #%%---------------------------
class net:
   
    def __init__(self, inputs, output_size, layers, dropout, lr, opt, cosine_lossmargin, pos, neg):
        
        # Features
        self.inputs = inputs  #self.embed = nn.Embedding.from_pretrained(inputs)
        users, input_size = inputs.shape

        # Define the model
        self.net = neuralnet(input_size, output_size, layers, dropout)

        # Define the optimizer
        self.lr = lr
        self.optimizer = getattr(torch.optim, opt)(self.net.parameters(), self.lr)

        # Loss function
        self.margin = cosine_lossmargin
        #self.lossfn = lossfn
        self.loss_values = []

        # Training samples
        self.pos = torch.tensor(list(zip(*pos))) #pos = tuple(zip(pos[0],pos[1]))
        self.neg = torch.tensor(list(zip(*neg)))
        
        self.input1 = torch.cat((self.pos[0], self.neg[0]))
        self.input2 = torch.cat((self.pos[1], self.neg[1]))
        self.target = torch.cat((torch.ones(len(self.pos[0])), torch.ones(len(self.neg[0]))*-1))

    def lossfunc(self, newemb, margin):
        return F.cosine_embedding_loss(newemb[self.input1], newemb[self.input2], self.target, margin)

    def train(self, epochs, lossth):
        for i in range(epochs+1):
            newemb = self.net(self.inputs)
            loss = self.lossfunc(newemb, self.margin)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if i%10 == 0:
                print('Epoch %d | Loss: %.4f' % (i, loss.item()))
            self.loss_values.append(loss.item())
            if loss.item() < lossth: 
                break

        plt.plot(self.loss_values)
        return newemb.detach()
    
    def eval(pos):
        pass



# %%
"""
Date: 22 May 2020
Goal: 02 Complete network and training.
Author: Harsha HN harshahn@kth.se
"""
#%%---------------
import torch
import torch.nn as nn
import torch.nn.functional as F
import pinconv
import matplotlib.pyplot as plt 
import itertools
import dgl
from importlib import reload; reload(pinconv)

##%%------------------
#Define a Graph Convolution Network
class PCN(nn.Module):
    def __init__(self, convdim, output_size, K):
        super(PCN, self).__init__()
        [in_feats, hidden_size, out_feats] = convdim
        # kernels
        self.bnorm_in = nn.BatchNorm1d(in_feats)
        self.bnorm_out= nn.BatchNorm1d(output_size)

        # self.pinconvs=nn.ModuleList([pinconv.PinConv(*i) for i in convdim])
        self.pinconvs = nn.ModuleList([
            pinconv.PinConv(in_feats, hidden_size, out_feats) for k in range(K) ])
        self.G = nn.Linear(out_feats, output_size)
        self.g = nn.Parameter(torch.Tensor(1))
        
        nn.init.xavier_uniform_(self.G.weight, gain=nn.init.calculate_gain('relu'))
        nn.init.constant_(self.G.bias, 0)
        nn.init.constant_(self.g, 1)
        
    def forward(self, g, inputs):
        h = self.bnorm_in(inputs)
        for i, pconv in enumerate(self.pinconvs):
            h = pconv(g, h)
        h = self.g * F.relu(self.G(h))
        h = self.bnorm_out(h)
        return h

##%%---------------------------
class gnet(nn.Module):

    def __init__(self, graph, nodeemb, convlayers, layers, output_size, dropout, lr, opt, select_loss, loss_margin, pos, neg, fdim=24):

        super(gnet, self).__init__()
        # Graph
        self.G = graph

        # Node embeddings
        if nodeemb != None:
            nodesize, fdim = nodeemb.shape
            self.embed = nn.Embedding.from_pretrained(nodeemb)
            print('Embeddings are loaded from the input')
        else:
            nodesize, fdim = self.G.number_of_nodes(), fdim
            self.embed = nn.Embedding(nodesize, fdim)
            print('Embeddings are created in randn')
        
        # Training samples
        self.pos = torch.tensor(list(zip(*pos))) #pos = tuple(zip(pos[0],pos[1]))
        self.neg = torch.tensor(list(zip(*neg)))

        # Define the model
        self.net = PCN([fdim, *convlayers], output_size, layers) 

        # Define the optimizer
        self.optimizer = getattr(torch.optim, opt)(itertools.chain(self.net.parameters(), self.embed.parameters()), lr)

        # Loss function
        self.margin = loss_margin
        self.select_loss = select_loss
        self.loss_values = []
        
        if select_loss == 'cosine':
            self.input1 = torch.cat((self.pos[0], self.neg[0]))
            self.input2 = torch.cat((self.pos[1], self.neg[1]))
            self.target = torch.cat((torch.ones(len(self.pos[0])), torch.ones(len(self.neg[0]))*-1))
    
    # Loss funciton definitions
    def lossfunc(self, newemb, margin):
        if self.select_loss == 'cosine':
            return F.cosine_embedding_loss(newemb[self.input1], newemb[self.input2], self.target, margin)
        elif self.select_loss == 'pinsage':
            p = torch.mul(newemb[self.pos[0]], newemb[self.pos[1]]).sum(1).mean()
            n = torch.mul(newemb[self.neg[0]], newemb[self.neg[1]]).sum(1).mean()
            return F.relu(n - p + margin)
            
    def train(self, epochs, lossth):
        for epoch in range(epochs+1):
            newemb = self.net(self.G, self.embed.weight)
            loss = self.lossfunc(newemb, self.margin)

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # if epoch%10 == 0:
            print('Epoch %d | Loss: %.4f' % (epoch, loss.item()))
            self.loss_values.append(loss.item())
            if loss.item() < lossth: 
                break
        
        # import matplotlib.pyplot as plt 
        plt.plot(self.loss_values)
        return newemb.detach()
    
    def eval(pos):
        pass


# %%
