# Verifying Jupyter Kernel

The "Python (runawayguys)" kernel has been installed. If it doesn't appear in Jupyter:

## Steps to Make Kernel Visible:

1. **Restart Jupyter Lab/Notebook**
   - Close all Jupyter windows
   - Restart Jupyter Lab or Jupyter Notebook

2. **Refresh Kernel List**
   - In Jupyter Lab: Go to Settings → Advanced Settings → Kernel → Refresh
   - Or restart the Jupyter server

3. **Select Kernel in Notebook**
   - Open your notebook
   - Click on the kernel name (top right)
   - Select "Python (runawayguys)" from the list

4. **If Still Not Visible:**
   - Try: Kernel → Change Kernel → Select "Python (runawayguys)"
   - Or restart your computer (sometimes needed for Windows)

## Verify Installation:

Run this command to verify the kernel is installed:
```bash
jupyter kernelspec list
```

You should see:
```
runawayguys    C:\Users\Pelin\AppData\Roaming\jupyter\kernels\runawayguys
```

## Alternative: Reinstall Kernel

If the kernel still doesn't appear, try uninstalling and reinstalling:
```bash
jupyter kernelspec uninstall runawayguys -y
python -m ipykernel install --user --name=runawayguys --display-name "Python (runawayguys)"
```

This will remove and reinstall the kernel.

