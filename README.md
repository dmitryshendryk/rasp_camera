# Backing up your Raspberry Pi SD Card on Windows

https://pimylifeup.com/backup-raspberry-pi/

# Backup up your Raspberry Pi SD Card on OS X

```
diskutil list
sudo dd if=/dev/disk1 of=~/PiSDBackup.dmg
```

# Restoring your Raspberry Pi Backup on OS X

```
diskutil list
diskutil unmountDisk /dev/disk1
sudo diskutil eject /dev/rdisk3
```


# Setup WIFI 

sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
sudo wpa_cli -i wlan0 reconfigure