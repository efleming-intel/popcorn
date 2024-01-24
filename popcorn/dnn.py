class dnn_log:
    def __init_(self):
        self.filename = ''
        self.data = None
        self.exec_data = None
        self.with_timestamp = True
        return

    def load_csv_log(self, log):
        self.filename = log
        self.with_timestamp = True
        data = self.load_dnnl_log()
        self.data = data

        return data


    def load_dnnl_log(self):
        import csv
        data = []

        with open(self.filename) as f:
            for line in csv.DictReader(f, fieldnames=('onednn_verbose','timestamp','backend','exec','arch','type', 'kernel', 'pass', 'fmt', 'opt', 'alg', 'shape', 'time', 'dummy')):
                if(line['timestamp'] in ['info', 'graph', 'primitive']):
                    # break if it is a info line, not needed
                    continue
                else:
                    data.append(line)
        return data
