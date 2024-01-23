import pandas as pd


class dnn_log:
    def __init_(self):
        self.filename = ''
        self.data = None
        self.exec_data = None
        self.with_timestamp = True
        return

    def load_csv_log(self, log):
        print("call to load_csv_log")
        self.filename = log
        self.with_timestamp = True
        data = self.load_log_dnnl_timestamp_backend()
        count = data['time'].count()
        print("finished load_log_dnnl_timestamp_backend(log)")
       
        if count <= 1:
            data = self.load_log_dnnl_timestamp()
            count = data['time'].count()
            self.with_timestamp = True
        
            if data['time'].count() <= 1:
                print("ONEDNN_VERBOSE_TIMESTAMP MISSING")
                return 0

        exec_data = data[data['exec'] == 'exec']
        self.data = data
        self.exec_data = exec_data.copy()

        return data

    def load_log_dnnl_timestamp(self):
        # dnnl_verbose,629411020589.218018,exec,cpu,convolution,jit:avx2,forward_inference,src_f32::blocked:abcd:f0 wei_f32::blocked:Acdb8a:f0 bia_f32::blocked:a:f0 dst_f32::blocked:aBcd8b:f0,,alg:convolution_direct,mb1_ic3oc96_ih227oh55kh11sh4dh0ph0_iw227ow55kw11sw4dw0pw0,1.21704
        print("load_log_dnnl_timestamp")
        print(self.filename)
        data = pd.read_csv(self.filename, names=[ 'dnnl_verbose','timestamp','exec','arch','type', 'jit', 'pass', 'fmt', 'opt', 'alg', 'shape', 'time', 'dummy'], engine='python')
        
        return data

    def load_log_dnnl_timestamp_backend(self):
        print("oad_log_dnnl_timestamp_backend")
        print(self.filename)
        #"onednn_verbose,operation,engine,primitive,implementation,prop_kind,memory_descriptors,attributes,auxiliary,problem_desc"
        # dnnl_verbose,629411020589.218018,primitive,exec,cpu,convolution,jit:avx2,forward_inference,src_f32::blocked:abcd:f0 wei_f32::blocked:Acdb8a:f0 bia_f32::blocked:a:f0 dst_f32::blocked:aBcd8b:f0,,alg:convolution_direct,mb1_ic3oc96_ih227oh55kh11sh4dh0ph0_iw227ow55kw11sw4dw0pw0,1.21704
        data = pd.read_csv(self.filename, names=[ 'dnnl_verbose','timestamp','backend','exec','arch','type', 'jit', 'pass', 'fmt', 'opt', 'alg', 'shape', 'time', 'dummy'], engine='python')
        
        return data