import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class Linear(nn.Module):
    def __init__(self, in_features, out_features, bias=True, mle=False, logvar_init=-8.0):
        super().__init__()
        self.mle = mle
        self.in_features = in_features
        self.out_features = out_features
        self.weight_mean = nn.Parameter(torch.Tensor(out_features, in_features))
        self.weight_logvar = nn.Parameter(torch.Tensor(out_features, in_features))
        self.logvar_init = logvar_init
        if bias:
            self.bias_mean = nn.Parameter(torch.Tensor(out_features))
            self.bias_logvar = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias_mean', None)
            self.register_parameter('bias_logvar', None)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight_mean, a=math.sqrt(5))
        nn.init.constant_(self.weight_logvar, self.logvar_init)
        if self.bias_mean is not None:
            nn.init.zeros_(self.bias_mean)
            nn.init.constant_(self.bias_logvar, self.logvar_init)

    def forward(self, x, num_param_samples=10):
        if self.mle:
            return F.linear(x, self.weight_mean, self.bias_mean)

        x = x.reshape(num_param_samples, -1, *x.shape[1:])

        def param_sample(x):
            weight_std = torch.exp(0.5 * self.weight_logvar)
            weight = self.weight_mean + weight_std * torch.randn_like(weight_std)
            bias = None
            if self.bias_mean is not None:
                bias_std = torch.exp(0.5 * self.bias_logvar)
                bias = self.bias_mean + bias_std * torch.randn_like(bias_std)

            return F.linear(x, weight, bias)

        out = torch.vmap(param_sample, in_dims=0, randomness='different')(x)
        out = out.reshape(-1, *out.shape[2:])
        return out



class Conv2d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, bias=True, mle=False, logvar_init=-8.0):
        super().__init__()
        self.mle = mle
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.weight_mean = nn.Parameter(torch.Tensor(out_channels, in_channels, kernel_size, kernel_size))
        self.weight_logvar = nn.Parameter(torch.Tensor(out_channels, in_channels, kernel_size, kernel_size))
        self.logvar_init = logvar_init
        if bias:
            self.bias_mean = nn.Parameter(torch.Tensor(out_channels))
            self.bias_logvar = nn.Parameter(torch.Tensor(out_channels))
        else:
            self.register_parameter('bias_mean', None)
            self.register_parameter('bias_logvar', None)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight_mean, a=math.sqrt(5))
        nn.init.constant_(self.weight_logvar, self.logvar_init)
        if self.bias_mean is not None:
            nn.init.zeros_(self.bias_mean)
            nn.init.constant_(self.bias_logvar, self.logvar_init)

    def forward(self, x, num_param_samples=10):
        if self.mle:
            return F.conv2d(x, self.weight_mean, self.bias_mean, stride=self.stride, padding=self.padding)

        x = x.reshape(num_param_samples, -1, *x.shape[1:])

        def param_sample(x):
            weight_std = torch.exp(0.5 * self.weight_logvar)
            weight = self.weight_mean + weight_std * torch.randn_like(weight_std)
            bias = None
            if self.bias_mean is not None:
                bias_std = torch.exp(0.5 * self.bias_logvar)
                bias = self.bias_mean + bias_std * torch.randn_like(bias_std)
            return F.conv2d(x, weight, bias, stride=self.stride, padding=self.padding)

        out = torch.vmap(param_sample, in_dims=0, randomness='different')(x)
        out = out.reshape(-1, *out.shape[2:])
        return out


class ConvTranspose2d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, bias=True, mle=False, logvar_init=-8.0):
        super().__init__()
        self.mle = mle
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.weight_mean = nn.Parameter(torch.Tensor(in_channels, out_channels, kernel_size, kernel_size))
        self.weight_logvar = nn.Parameter(torch.Tensor(in_channels, out_channels, kernel_size, kernel_size))
        self.logvar_init = logvar_init
        if bias:
            self.bias_mean = nn.Parameter(torch.Tensor(out_channels))
            self.bias_logvar = nn.Parameter(torch.Tensor(out_channels))
        else:
            self.register_parameter('bias_mean', None)
            self.register_parameter('bias_logvar', None)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight_mean, a=math.sqrt(5))
        nn.init.constant_(self.weight_logvar, self.logvar_init)
        if self.bias_mean is not None:
            nn.init.zeros_(self.bias_mean)
            nn.init.constant_(self.bias_logvar, self.logvar_init)

    def forward(self, x, num_param_samples=10):
        if self.mle:
            return F.conv_transpose2d(x, self.weight_mean, self.bias_mean, stride=self.stride, padding=self.padding)

        x = x.reshape(num_param_samples, -1, *x.shape[1:])

        def param_sample(x):
            weight_std = torch.exp(0.5 * self.weight_logvar)
            weight = self.weight_mean + weight_std * torch.randn_like(weight_std)
            bias = None
            if self.bias_mean is not None:
                bias_std = torch.exp(0.5 * self.bias_logvar)
                bias = self.bias_mean + bias_std * torch.randn_like(bias_std)
            return F.conv_transpose2d(x, weight, bias, stride=self.stride, padding=self.padding)

        out = torch.vmap(param_sample, in_dims=0, randomness='different')(x)
        out = out.reshape(-1, *out.shape[2:])
        return out


class BatchNorm2d(nn.Module):
    def __init__(self, num_features, mle=False, logvar_init=-8.0):
        super().__init__()
        self.mle = mle
        self.num_features = num_features
        self.weight_mean = nn.Parameter(torch.Tensor(num_features))
        self.weight_logvar = nn.Parameter(torch.Tensor(num_features))
        self.bias_mean = nn.Parameter(torch.Tensor(num_features))
        self.bias_logvar = nn.Parameter(torch.Tensor(num_features))
        self.logvar_init = logvar_init
        self.reset_parameters()

        self.register_buffer('running_mean', torch.zeros(num_features))
        self.register_buffer('running_var', torch.ones(num_features))

        self.momentum = 0.1
        self.eps = 1e-5

    def reset_parameters(self):
        nn.init.ones_(self.weight_mean)
        nn.init.constant_(self.weight_logvar, self.logvar_init)
        nn.init.zeros_(self.bias_mean)
        nn.init.constant_(self.bias_logvar, self.logvar_init)

    def forward(self, x, num_param_samples=10):
        if self.training:
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * x.mean([0, 2, 3])
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * x.var([0, 2, 3], unbiased=True)

        running_mean = self.running_mean.reshape(1, 3, 1, 1)
        running_var = self.running_var.reshape(1, 3, 1, 1)
        weight_mean = self.weight_mean.reshape(1, 3, 1, 1)
        weight_logvar = self.weight_logvar.reshape(1, 3, 1, 1)
        bias_mean = self.bias_mean.reshape(1, 3, 1, 1)
        bias_logvar = self.bias_logvar.reshape(1, 3, 1, 1)

        if self.mle:
            return (x - running_mean) / torch.sqrt(running_var + self.eps) * weight_mean + bias_mean

        x = x.reshape(num_param_samples, -1, *x.shape[1:])

        def param_sample(x):
            weight_std = torch.exp(0.5 * weight_logvar)
            weight = weight_mean + weight_std * torch.randn_like(weight_std)
            bias_std = torch.exp(0.5 * bias_logvar)
            bias = bias_mean + bias_std * torch.randn_like(bias_std)

            return (x - running_mean) / torch.sqrt(running_var + self.eps) * weight + bias

        out = torch.vmap(param_sample, in_dims=0, randomness='different')(x)
        out = out.reshape(-1, *out.shape[2:])
        return out