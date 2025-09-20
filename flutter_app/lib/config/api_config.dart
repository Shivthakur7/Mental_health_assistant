class ApiConfig {
  // 🚀 CHANGE THIS TO YOUR AZURE VM'S PUBLIC IP ADDRESS
  // Example: 'http://20.123.45.67:8000' (replace with your actual VM IP)
  static const String baseUrl = 'http://20.40.56.114:8000';
  
  // Alternative configurations for different environments
  static const String localUrl = 'http://127.0.0.1:8000';
  static const String androidEmulatorUrl = 'http://10.0.2.2:8000';
  
  // 📝 Instructions:
  // 1. After creating your Azure VM, get the public IP address
  // 2. Replace the baseUrl above with: 'http://YOUR_VM_PUBLIC_IP:8000'
  // 3. Make sure port 8000 is open in Azure Network Security Group
  // 4. Rebuild your Flutter app after making this change
  
  // Example:
  // static const String baseUrl = 'http://20.123.45.67:8000';
}
