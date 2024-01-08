import torch
from awave.filtermodel import FilterConv
from visualization import *
from config import *
from icecream import ic

awt = torch.load("models/awave.transform1d__BATCH-32__EPOCH-256__DATA-LR=1e-3__Reconstruction-Loss-Only__FILTER-6__TIME-1704721743.731563.pth")
model = awt.filter_model
model.to(DEVICE)

data = torch.load(DATA_PATH)
x = torch.split(data, min(BATCH_SIZE*5, data.size(0)), 0)

ic(data.shape, x[0].shape)

ic(model)

y = model(x[0])

ic(len(x[0]))
print("Out shape:", y.shape)

for id in range(100, 160):
    h0 = y[id]
    sig = x[0][id]
    # plot_waveform(sig,4100)
    # ic(filter)
    high = torch.reshape(low_to_high(torch.reshape(h0, [1, 1, h0.size(0)])),[h0.size(0)])
    low = h0
    # plot_filter_banks(low, high)
    plotdiag(low, high, sig, 4100)
    break




# Correct Code Form forward paralleliztion!!
""" 
import torch
import torch.nn.functional as F

# Input shape: (B, C, H, W), B = batch size
input = torch.rand([32, 1, 1, 1024])  # Small batch size and length for illustration
filters = torch.rand([32, 2, 1, 1, 10])
print("Input:")
print(input.shape)
print("\nFilters:")
print(filters.shape)

lohi = F.conv2d(input, filters[0], padding=(0, 8), stride=(1, 2), groups=1)

# Reshape input to (B, C, H*W)
input = input.view(32, 1, 1024)

# Reshape filters to (out_channels, in_channels, kH, kW)
filters = filters.view(32 * 2, 1, 1, 10)


# Apply 2D convolution with groups=2
output = F.conv2d(input, filters, stride=(1, 2), padding=(0, 8), groups=32)

# Reshape output to (batch, out_channels, C, H, W)
output = output.view(32, 2, output.size(1), output.size(2))

# Print input, filters, and output for illustration
print("\nOutput:")
print(output.shape)
print(lohi.shape)

max_abs_diff = torch.max(torch.abs(lohi[0] - output[0]))

# Print the maximum absolute difference
print("\nMaximum Absolute Difference:", max_abs_diff.item())

assert torch.allclose(lohi[0], output[0], atol=1e-6)
"""

"""
import torch
import torch.nn.functional as F

# Input shape: (B, C, H, W), B = batch size
input = torch.rand([32, 1, 1, 40])  # Small batch size and length for illustration
filters = torch.rand([32, 1, 1, 1, 10])
print("Input:")
print(input.shape)
print("\nFilters:")
print(filters.shape)

lohi = F.conv_transpose2d(input, filters[0], stride=(1, 2), padding=(0, 8), groups=1)

# Reshape input to (B, C, H*W)
input = input.view(32, 1,  40)
# Reshape filters to (in_channels * out_channels, 1, kH, kW)
filters = filters.view(32*1, 1, 1, 10)
# Apply transposed 2D convolution with groups=in_channels*out_channels
output = F.conv_transpose2d(input, filters, stride=(1, 2), padding=(0, 8), groups=32)
# Reshape output to (batch, out_channels, C, H, W)
output = output.view(32, 1, output.size(1), output.size(2))

# Print input, filters, and output for illustration
print("\nOutput:")
print(output.shape)
print(lohi.shape)

max_abs_diff = torch.max(torch.abs(lohi[0] - output[0]))

# Print the maximum absolute difference
print("\nMaximum Absolute Difference:", max_abs_diff.item())

assert torch.allclose(lohi[0], output[0], atol=1e-6)
"""

# mod = torch.rand([1,1,10])
# print(mod)
# print(mod[:,:,:5])
# print(mod[:,:,5:])


# awt = torch.load('models/awave.filtermodel__BATCH-32__EPOCH-2__DATA-ADCF__FILTER-6__TIME-1704713867.891409.pth')
# print(awt.filter_model.parameters())


