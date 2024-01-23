import pandas as pd


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

    def load_log_dnnl_timestamp(self):
        # dnnl_verbose,629411020589.218018,exec,cpu,convolution,jit:avx2,forward_inference,src_f32::blocked:abcd:f0 wei_f32::blocked:Acdb8a:f0 bia_f32::blocked:a:f0 dst_f32::blocked:aBcd8b:f0,,alg:convolution_direct,mb1_ic3oc96_ih227oh55kh11sh4dh0ph0_iw227ow55kw11sw4dw0pw0,1.21704
        data = pd.read_csv(self.filename, names=[ 'dnnl_verbose','timestamp','exec','arch','type', 'jit', 'pass', 'fmt', 'opt', 'alg', 'shape', 'time', 'dummy'], engine='python')
        
        return data

    def load_log_dnnl_timestamp_backend(self):
        #"onednn_verbose,operation,engine,primitive,implementation,prop_kind,memory_descriptors,attributes,auxiliary,problem_desc"
        # dnnl_verbose,629411020589.218018,primitive,exec,cpu,convolution,jit:avx2,forward_inference,src_f32::blocked:abcd:f0 wei_f32::blocked:Acdb8a:f0 bia_f32::blocked:a:f0 dst_f32::blocked:aBcd8b:f0,,alg:convolution_direct,mb1_ic3oc96_ih227oh55kh11sh4dh0ph0_iw227ow55kw11sw4dw0pw0,1.21704
        data = pd.read_csv(self.filename, names=[ 'dnnl_verbose','timestamp','backend','exec','arch','type', 'jit', 'pass', 'fmt', 'opt', 'alg', 'shape', 'time', 'dummy'], engine='python')
        
        return data
    

    def load_dnnl_log(self):
        import csv
        data = []

        with open(self.filename) as f:
            for line in csv.DictReader(f, fieldnames=('onednn_verbose','timestamp','backend','exec','arch','type', 'kernel', 'pass', 'fmt', 'opt', 'alg', 'shape', 'time', 'dummy')):
                if(line['timestamp'] in ['info', 'graph', 'primitive']):
                    continue
                else:
                    data.append(line)
                    print(line)
        return data
