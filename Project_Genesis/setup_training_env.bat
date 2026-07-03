@echo off
echo [1/3] Installing PyTorch (CUDA 12.1)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo [2/3] Installing Unsloth and basic dependencies...
pip install --no-deps unsloth xformers trl peft accelerate bitsandbytes

echo.
echo [3/3] Installing remaining dependencies from requirements_training.txt...
pip install -r requirements_training.txt

echo.
echo Setup Complete! Please try running 'python train_genesis.py' again.
pause
