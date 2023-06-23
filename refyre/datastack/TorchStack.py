
with optional_dependencies("warn"):
    import torch
    from torch.utils.data import Dataset

    class TorchStack(Dataset):
        def __init__(self, association):
            self.association = association

        def __len__(self):
            return len(self.association)

        def items(self, k):
            return self.association[k]