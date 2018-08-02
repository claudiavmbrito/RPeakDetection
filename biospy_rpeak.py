from biosppy.signals import ecg
import wfdb
import csv
import numpy

def filtrar_ler(f):
    # read signal

    sig, fields = wfdb.srdsamp(f, channels=[0])
    allrecord = wfdb.rdsamp(f, channels=[0], physical=False)
    # time discrete signal -> numpy array
    xall = allrecord.d_signals[:, 0]
    # freq at which the signal is sampled
    fs = fields['fs']
    print("frequencia = " + str(fs))
    return xall, fs


def rlocationindeces(f):
    signal, fs = filtrar_ler(f)
    out = ecg.hamilton_segmenter(signal=signal, sampling_rate=fs)
    return f, out


def returning_all(f):
    signal, fs = filtrar_ler(f)
    out = ecg.ecg(signal=signal, sampling_rate=fs, show=False)
    ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate = out
    return f, ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate


def heartbeats(f):
    signal, fs = filtrar_ler(f)
    x, ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate = returning_all(f)
    out = ecg.extract_heartbeats(signal=signal, rpeaks=rpeaks, sampling_rate=fs, before=0.2, after=0.4)
    return f, out


def comparisons(f):
    signal, fs = filtrar_ler(f)
    x, ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate = returning_all(f)
    out = ecg.compare_segmentation(reference=rpeaks, test=rpeaks, sampling_rate=fs, offset=0, minRR=None, )
    return out


def detectrr(f):
    x, ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate = returning_all(f)
    rr = []
    for i in range(len(rpeaks) - 1):
        xx = rpeaks[i + 1] - rpeaks[i]
        rr.append(xx)
        i = i + 1
    return x, rpeaks, rr, heart_rate


def features_calculation(f):
    x, rpeaks, rr, heart_rate = detectrr(f)
    mean_hr = numpy.mean(heart_rate)
    max_hr = numpy.max(heart_rate)
    min_hr = numpy.min(heart_rate)
    median_hr = numpy.median(heart_rate)
    range_hr = numpy.ptp(heart_rate)
    mean_rr = numpy.mean(rr)
    max_rr = numpy.max(rr)
    min_rr = numpy.min(rr)
    median_rr = numpy.median(rr)
    range_rr = numpy.ptp(rr)
    return mean_hr, max_hr, min_hr, median_hr, range_hr, mean_rr, max_rr, min_rr, median_rr, range_rr


def save_file(f, rpeaks, heart_rate):
    with open('biosppy_test.csv', 'a', newline='') as csvfile:
        extraction_features = csv.writer(csvfile, delimiter=';',
                                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
        extraction_features.writerow([f, rpeaks, heart_rate])
        csvfile.close()


'''
def main(f):
    x,y,z,w = detectrr(f)
    save_file(x, z, w)


if __name__ == '__main__':

    for i in range(0, 10):
        name = path
        print('\n ECG Mit-BIH Arrhythmia database record: ' + str(i) + '\n')
        main(name)

    main('27007664')

x, y, z, w, v, a, b, c, d, e = features_calculation('27007664')
print("Mean heart rate = " + str(x))
print("Max heart rate = " + str(y))
print("Min heart rate = " + str(z))
print("Median heart rate = " + str(w))
print("Range heart rate = " + str(v))
print("Mean RR interval = " + str(a))
print("Max RR interval = " + str(b))
print("Min RR interval = " + str(c))
print("Median RR interval = " + str(d))
print("Range RR interval = " + str(e))
'''

x, rpeaks, rr, heart_rate = detectrr(path/to/data)
print(rpeaks)
print(len(rpeaks))
