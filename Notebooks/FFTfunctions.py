import numpy as np # numerical computing commands
import scipy.signal as signal

# FFT Function
def avgFFT(sig,
           sample_rate,
           resolution = 1,
           number_of_windows = 1,
           overlap = 0.3,
           window_type = 'hann',
           mode = 'avg'
          ):   
    signal_samples = len(sig) # total number of samples in entire recording
    samples_per_window = int(sample_rate/resolution) # number of samples per window

    # Initialising the matrices required
    sig_matrix = np.zeros((number_of_windows, samples_per_window)) # Initialise the shape of signal matrix
    sig_fft = np.zeros((number_of_windows, samples_per_window), dtype = np.complex_) # Initialise the shape of the fft matrix
    
    # Calculate the number of samples required based on the number of windows specified
    samples_required = samples_per_window + ((1 - overlap) * samples_per_window) * (number_of_windows - 1)
    
    # Calculate the maximum number of windows possible for the recording
    max_windows = int(np.floor(((signal_samples - samples_per_window)/((1 - overlap) * samples_per_window)) + 1))
    
    print(f'The maximum number of windows for these parameters is {max_windows}')
    
    ## Put each window of the signal into a row of sig_matrix ##
    if signal_samples < samples_required: # Checks if the number of samples created from given arguments is possible to be windowed
        raise ValueError(f'The number of windows specified is too large for the recording. The maximum number of windows for this recording with a resolution of {int(resolution)} Hz and overlap of {int(overlap * 100)}% is {max_windows}.')
        return
    else:
        for ii in range(number_of_windows):
            start_index = int(round(samples_per_window * ii * (1 - overlap)))
            end_index = start_index + samples_per_window
            sig_matrix[ii,:] = sig[start_index: end_index]

    # Window Type    
    if window_type == "uniform":
        window_function = np.ones([samples_per_window])
    elif window_type == "hamming":
        window_function = signal.hamming(samples_per_window)
    elif window_type == "hanning":
        window_function = signal.hanning(samples_per_window)
    elif window_type == "flattop":
        window_function = signal.flattop(samples_per_window)
    elif window_type == "hann":
        window_function = signal.hann(samples_per_window)
    else:
        print("Not a valid windowing function. Using a Hann window.")
        window_function = signal.hann(samples_per_window)  
        
    # Window the signal by multiplying signal to the window
    sig_matrix = np.multiply(sig_matrix, window_function)
    print('The signals have been windowed successfully')

    # Take the FFT of each row, and substitute to the row
    for ii in range(number_of_windows):
        sig_fft[ii,:] = np.fft.fft(sig_matrix[ii,:])/samples_per_window # This process includes normalisation (divided by number of samples)

    sig_fft = sig_fft[0:number_of_windows + 1, 0:int(samples_per_window/2)] # only use half of the range (Fourier analysis - remove the mirrored part)
    sig_fft = np.sum(abs(sig_fft), axis = 0)/number_of_windows # Averaging the absolute values of FFT
    print('avgFFT function operation successful')
    return sig_fft

def sigrms(s):
    return np.sqrt(np.mean(s**2))