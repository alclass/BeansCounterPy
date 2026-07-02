"""
sudo locale-gen pt_BR.UTF-8
sudo update-locale
# for Docker files
RUN apt-get update && apt-get install -y locales \
    && locale-gen pt_BR.UTF-8
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV LC_ALL pt_BR.UTF-8
# =====================
import subprocess

# Run the system command to list available locales
result = subprocess.run(["locale", "-a"], capture_output=True, text=True)
locales = result.stdout.splitlines()

print(locales)

"""

import locale

# Get all alias names recognized by Python
all_aliases = list(locale.locale_alias.keys())
for ali in all_aliases:
  if ali.lower().startswith('pt'):
    print(ali)
