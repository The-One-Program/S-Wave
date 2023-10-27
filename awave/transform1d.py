import torch
import torch.nn as nn

from awave.utils import lowlevel
from awave.transform import AbstractWT
from awave.utils.misc import init_filter, low_to_high



class DWT1d(AbstractWT):
    '''Class of 1d wavelet transform:

    Params
    ------
    * J: int;
        number of levels of decomposition.

    * wave: str;
        which wavelet to use.
        can be:
            1) a string to pass to pywt.Wavelet constructor
            2) a pywt.Wavelet class
            3) a tuple of numpy arrays, either (h0, h1) or (h0_col, h1_col, h0_row, h1_row)

    * mode: str;
        'zero', 'symmetric', 'reflect' or 'periodization'. The padding scheme
    * filter_model: nn.Module;
        A Predefine nn.Module object for determnining filters as a model
    '''

    # The default values are mentioned.
    def __init__(self, wave='db3',filter_model = None, mode='zero', J=5, init_factor=1, noise_factor=0, const_factor=0, device='cpu'):
        super().__init__()

        self.filter_model = filter_model

        # Load the wavelet from pywt
        h0, _ = lowlevel.load_wavelet(wave)
        
        # initialize by adding random noise
        h0 = init_filter(h0, init_factor, noise_factor, const_factor)

        # parameterize as a gradient-tensor
        self.h0 = nn.Parameter(h0, requires_grad=True, device=self.device)
        

        # Replacing the Filters with a CNN model
        # sefl.h0 = CNN_Model
        self.h0 = self.h0.to(device)
        self.J = J
        self.mode = mode
        self.wt_type = 'DWT1d'
        self.device = device

    def forward(self, x):

        """ Forward pass of the DWT1d.

        Args:
            x (tensor): Input of shape: (N{Batch size}, in_C{input_channel}, in_L{input_Length of signal})

        Returns:
            (yl, yh)
                tuple of lowpass (yl) and bandpass (yh) coefficients.
                yh is a list of length J with the first entry
                being the finest scale coefficients.
        """

        assert x.ndim == 3, "Can only handle 3d inputs (N, in_C, in_L)"

        highs = ()
        x0 = x

        # Solve the need of 2 functions i.e mode_to_int and int_to_mode by making it an enum
        mode = lowlevel.mode_to_int(self.mode)


        # Getting the filter from the model:
        if self.filter_model is not None:
            self.h0 = self.filter_model(x)
            
        h1 = low_to_high(self.h0)

        # Do a multilevel transform
        for j in range(self.J):
            x0, x1 = lowlevel.AFB1D.forward(x0, self.h0, h1, mode)
            highs += (x1,)

        return (x0,) + highs

    def inverse(self, coeffs):

        """
        Args:
            coeffs (yl, yh): tuple of lowpass and bandpass coefficients, should
              match the format returned by DWT1DForward.

        Returns:
            Reconstructed input of shape :math:`(N, C_{in}, L_{in})`

        Note:
            Can have None for any of the highpass scales and will treat the
            values as zeros (not in an efficient way though).
        """
        
        coeffs = list(coeffs)
        x0 = coeffs.pop(0)
        highs = coeffs
        assert x0.ndim == 3, "Can only handle 3d inputs (N, C, L)"
        mode = lowlevel.mode_to_int(self.mode)

        h1 = low_to_high(self.h0)
        # Do a multilevel inverse transform
        for x1 in highs[::-1]:
            if x1 is None:
                x1 = torch.zeros_like(x0)

            # 'Unpad' added signal
            if x0.shape[-1] > x1.shape[-1]:
                x0 = x0[..., :-1]
            x0 = lowlevel.SFB1D.forward(x0, x1, self.h0, h1, mode)
        return x0
