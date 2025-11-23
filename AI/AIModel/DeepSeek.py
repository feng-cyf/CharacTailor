from AIModel.DouBaoLite import DouBaoLite


class DeepSeek(DouBaoLite):
    def __init__(self):
        super(DeepSeek, self).__init__()
        self.model="deepseek-v3-1-250821"