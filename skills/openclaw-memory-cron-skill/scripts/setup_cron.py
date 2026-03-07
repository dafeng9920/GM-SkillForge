import os
import subprocess
import getpass

def setup_cron(project_dir="/root/openclaw-box", hour=3, minute=0):
    user = getpass.getuser()
    script_path = os.path.join(project_dir, "skills/openclaw-memory-cron-skill/scripts/auto_clean.sh")
    
    # Cron line: minute hour * * * /bin/bash /path/to/script project_dir
    cron_cmd = f"{minute} {hour} * * * /bin/bash {script_path} {project_dir} >> /var/log/openclaw-autoclean.log 2>&1\n"
    
    try:
        # Read existing crontab
        current_cron = subprocess.check_output("crontab -l", shell=True, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError:
        current_cron = ""

    if script_path in current_cron:
        print("Cron job already exists. Updating...")
        # Simple update: filter out old and add new
        lines = [line for line in current_cron.splitlines() if script_path not in line]
        new_cron = "\n".join(lines) + "\n" + cron_cmd
    else:
        new_cron = current_cron + "\n" + cron_cmd

    # Write back
    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
    process.communicate(input=new_cron.encode())
    
    print(f"Successfully scheduled OpenClaw Auto-Clean at {hour:02d}:{minute:02d} daily.")

if __name__ == "__main__":
    setup_cron()
