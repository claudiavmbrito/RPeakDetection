import wfdb
import scipy
import numpy
import matplotlib.pyplot as plt
import csv
from hrv.filters import moving_average

def peaks_hr(x, peaks_indexes, fs, title, figsize=(40, 10), saveto=None):
    hrs = wfdb.processing.compute_hr(siglen=x.shape[0], peak_indices=peaks_indexes, fs=fs)

    N = x.shape[0]

    fig, ax_left = plt.subplots(figsize=figsize)
    ax_right = ax_left.twinx()

    ax_left.plot(x, color='#3979f0', label='Signal')
    ax_left.plot(peaks_indexes, x[peaks_indexes], 'rx', marker='x', color='#8b0000', label='Peak', markersize=12)
    #ax_right.plot(numpy.arange(N), hrs, label='Heart rate', color='m', linewidth=2)

    ax_left.set_title(title)

    ax_left.set_xlabel('Time (ms)')
    ax_left.set_ylabel('ECG', color='#3979f0')
    ax_right.set_ylabel('Heart rate (bpm)', color='m')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax_left.tick_params('y', colors='#3979f0')
    ax_right.tick_params('y', colors='m')
    if saveto is not None:
        plt.savefig(saveto, dpi=600)
    plt.show()


def gqrs_plot(f, t0=0, tf=1000):

    sig, fields = wfdb.srdsamp(f, sampfrom=t0, sampto=tf, channels=[0])
    allrecord = wfdb.rdsamp(f, channels=[0], physical=False)
    record = wfdb.rdsamp(f, sampfrom=t0, sampto=tf, channels=[0], physical=False)
    x = record.d_signals[:, 0]
    xall = allrecord.d_signals[:, 0]
    fs = fields['fs']
    print("frequencia = "+ str(fs))
    nyq = 0.5 * fs
    highfreq = 45
    lowfreq = 0.5


    # baseline correction and bandpass filter of signals
    # hoping it works
    lowpass = scipy.signal.butter(1, highfreq / nyq, 'low')
    highpass = scipy.signal.butter(1, lowfreq / nyq, 'high')

    # could use an actual bandpass filter, maybe
    # new filter to 50hz, maybe
    ecg_low = scipy.signal.filtfilt(*lowpass, x=x)
    ecg_band = scipy.signal.filtfilt(*highpass, x=ecg_low)

    ecg_low_all = scipy.signal.filtfilt(*lowpass, x=xall)
    ecg_band_all = scipy.signal.filtfilt(*highpass, x=ecg_low_all)

    peaks_indexes = wfdb.processing.gqrs_detect(ecg_band, fs=fs, adcgain=record.adcgain[0],
                                                adczero=record.adczero[0], threshold=1.0)
    peaks_indexes2 = wfdb.processing.gqrs_detect(ecg_band_all, fs=fs, adcgain=record.adcgain[0],
                                                adczero=record.adczero[0], threshold=1.0)
    #print(peaks_indexes)
    #peaks_hr(ecg_band, peaks_indexes=peaks_indexes, fs=fs, title="GQRS peak detection on Data")
    min_bpm = 20  # podera ser diferente mas tem de ser normalizado para estes valores
    max_bpm = 230  # same
    min_gap = fs * 60 / min_bpm  # diferenca minima entre os valores tendo em conta a frequencia de corte detetada no exame
    max_gap = fs * 60 / max_bpm  # esta diferenca pode nao ter nada a ver com o resto
    peaks_indexes = wfdb.processing.correct_peaks(ecg_band, peak_indices=peaks_indexes, min_gap=min_gap,
                                                  max_gap=max_gap, smooth_window=150)

    peaks_indexes2 = wfdb.processing.correct_peaks(ecg_band_all, peak_indices=peaks_indexes2, min_gap=min_gap,
                                                  max_gap=max_gap, smooth_window=150)

    #a = sorted(peaks_indexes)
    b = sorted(peaks_indexes2)
    #print(a)
    print(b)

    #peaks_hr(ecg_band, peaks_indexes=a, fs=fs, title="Corrected GQRS peak detection on Data")
    allqrs = len(b)
    print('Complexos QRS presentes no total ', allqrs)
    return f, allqrs, b



def detectrr(f):
    x,allqrs,peaksindexes2 = gqrs_plot(f)
    rr = []
    for i in range(len(peaksindexes2)-1):
        xx = peaksindexes2[i+1]-peaksindexes2[i]
        rr.append(xx)
        i=i+1
    print(rr)
    return x, allqrs, rr





def save_file(f, allbeats, intervals):
    with open('ecg.csv', 'a', newline='') as csvfile:
        extraction_features = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        extraction_features.writerow([f, allbeats, intervals])
        csvfile.close()


def main(f):
    detectrr(f)

    #save_file(x,y,z)


if __name__ == '__main__':
#    for i in range(0, 1):
#        name = 'C:/Users/Asus/Desktop/tese/mit_bih/10' + str(i)
#        print('\n ECG Mit-BIH Arrhythmia database record: ' + str(i) + '\n')
#        main(name)
    main(path/to/data)

#fs= frequencia de amostragem -> 125hz t=1/fs

