{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
    pkgs.bash
    pkgs.libxcrypt
  ];
  
  env = {
    PYTHONPATH = ".";
    PORT = "8000";
  };
} 