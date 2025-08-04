from warnings import filterwarnings
import torch

# Suppress the 'pin_memory' warnings that appear on Apple-Silicon (MPS backend)
filterwarnings(
    "ignore",
    message=r".*pin_memory.*not supported on MPS.*",
    category=UserWarning,
    module=r"torch.utils.data.dataloader"
)

# Verify MPS support
if torch.backends.mps.is_available():
    print("M1 GPU is available and PyTorch is configured to use MPS!")
else:
    print("MPS backend is not available. Check your setup.")
