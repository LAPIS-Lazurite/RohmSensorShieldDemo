import subprocess

import sys
import time
import struct
import _thread as thread
from datetime import datetime

## Gateway Control
class SubghzError(Exception):
    def __init__(self,value,message):
        self.value=value
        self.message = message
    def __str__(self):
        return repr(self.message)
    
class Gateway():
    # API of gateway initialization
    # The function is called, when the gateway is declared.
    def __init__(self,sep,mode,callback=None):
        self.separator = sep
        self.start_flag = False
        self.dispMode = mode
        self.callback = callback
	
    #API for setting display mode
    #mode = 0: Serial Monitor
    #mode = 1: Binary Monitor
    def setDispMode(self,mode):
        self.dispMode = mode

    def Send(self,panid,rx_addr,payload):
        header=0xa821
        seq=0
        tx_addr=0
        if len(payload)>=230:            
            print("payload must be less than 241 bytes")
            raise SubghzError(1,"payload size over")
            return
        
#        raw = struct.pack("HBHHH%ds"%len(payload),header,0x00,panid,rx_addr,tx_addr,payload.encode('utf-8'))
        raw = struct.pack("9B%ds"%len(payload),int(header%256),int(header/256),seq,int(panid%256),int(panid/256),int(rx_addr%256),
                  int(rx_addr/256),int(tx_addr%256),int(tx_addr/256),payload.encode('utf-8'))
        status = True
        try:
            self.fpr.write(raw)
            time.sleep(0.05)
        except IOError :
            status = False
        if status == False:
            raise SubghzError(2,"Does not receive ack")
      
    # API to start gateway
    def start(self,ch,pwr,rate,panid,mode):
        self._load_driver(ch,pwr,rate,panid,mode)
        self._open_driver()

    # API to stop gateway
    def stop(self):
        self.start_flag = False

    # Unsupported Format
    # Frame control is not supported
    # Just pringint raw data
    def _mac802154_unsupported_format(self,raw,size,mode):
        if mode == 0:
            print(datetime.today(),"unsupported format::",raw)
        elif mode == 1:
            print(datetime.today(),"unsupported format::",sep=self.separator,end=self.separator)
            log_txt=""
            for i in range(0,size-1):
                log_txt += str("%02x"%struct.unpack_from('B',raw,i)[0])+self.separator
            print(log_txt)

    # Log Monitor
    def _BinaryMonitor(self,payload,size):
        msg = ""
        for i in range(0,size):
            msg += str("%02x"%struct.unpack_from('B',payload,i)[0])+self.separator
        return msg
    def _SerialMonitor(self,payload,size):
        return str(struct.unpack_from("%ds"%(size),payload,0))

    def _monitor(self,header,seq,rxPanid,rxAddr,txPanid,txAddr,rssi,payload,size):
        log_txt = ""
        log_txt += str(datetime.today()) + self.separator
        if header != None:
            log_txt += str("0x%04x"%header) + self.separator
        if seq != None:
            log_txt += str("0x%02x"%seq) + self.separator
        if rxPanid != None:
            log_txt += str("0x%04x"%rxPanid) + self.separator
        if rxAddr != None:
            log_txt += str("0x%04x"%rxAddr) + self.separator
        if txPanid != None:
            log_txt += str("0x%04x"%txPanid) + self.separator
        if txAddr != None:
            log_txt += str("0x%04x"%txAddr) + self.separator
        if rssi != None:
            log_txt += str("%03d"%rssi) + self.separator
        if payload != None:
            if self.dispMode == 0:
                log_txt += self._SerialMonitor(payload,size)
            elif self.dispMode == 1:
                log_txt += self._BinaryMonitor(payload,size)
        if self.dispMode != 2:
            print(log_txt)
        return

    #Mac Data Analysis
    def _mac(self,raw,size):
        seq = None
        txPanid = None
        txAddr = None
        rxPanid = None
        rxAddr = None
        payload = None
        rssi=None
        offset = 0
        header = struct.unpack_from('H',raw,offset)[0]
        offset += 2
        if header == 0xa821:
            seq = struct.unpack_from('B',raw,offset)[0]
            offset+= 1
            rxPanid = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            rxAddr = struct.unpack_from('H',raw,offset)[0]
            offset+=2
            txAddr = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            rssi = struct.unpack_from('B',raw,size-1)[0]
            payload = struct.unpack_from("%ds"%(size-offset-1),raw,offset)[0]
        elif header == 0xa802:
            seq = struct.unpack_from('B',raw,offset)[0]
            offset += 1
            rxPanid = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            rxAddr = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            txAddr = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            rssi = struct.unpack_from('B',raw,size-1)[0]
            payload = struct.unpack_from("%ds"%(size-offset-1),raw,offset)[0]
        elif header == 0x2801:
            seq = struct.unpack_from('B',raw,offset)[0]
            offset += 1
            rxPanid = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            rxAddr = struct.unpack_from('H',raw,offset)[0]
            offset += 2
            rssi = struct.unpack_from('B',raw,size-1)[0]
            payload = struct.unpack_from("%ds"%(size-offset-1),raw,offset)[0]
        else:
            self._mac802154_unsupported_format(raw,size,self.dispMode)
            return
        if(self.callback != None):
            self.callback(payload,size-offset-1)
        self._monitor(header,seq,rxPanid,rxAddr,txPanid,txAddr,rssi,payload,size-offset-1)
            
    # Main loop or gateway during operating
    def _loop(self):
        print("      date/time            headr  seq  rxPan  rxAddr txAddr rssi data b\'(text)\'")
        print("--------------------------|------|----|------|------|------|----|----------------")
        while self.start_flag:
            data=self.fpr.read(2)
            if data != b'':
                read_bytes = struct.unpack('H',data)[0]
                if read_bytes != 0:
                    data=self.fpr.read(read_bytes)
                    self._mac(data,read_bytes)
            time.sleep(0.001)
        self._close_driver()
        self._remove_driver()
    
    # loading driver and change attribution of driver
    def _load_driver(self,ch,pwr,rate,panid,mode):
        
        cmd = "sudo insmod /home/pi/driver/sub-ghz/DRV_802154.ko ch="+str(ch)+" rate="+str(rate)+" pwr="+str(pwr)+" panid="+hex(panid)+" mode="+hex(mode)
        print(cmd)
        try:
            ret = subprocess.check_output(cmd.split(" "))
        except subprocess.CalledProcessError:
            print("Driver may be loaded already..")
        except OSError:
             print("OSError")
        time.sleep(0.010)
        cmd = "sudo chmod 777 /dev/bp3596"
        ret = subprocess.check_output(cmd.split(" "))
      
        cmd = "tail -n 2 /var/log/messages"
        ret = subprocess.check_output(cmd.split(" "))
        print(ret.decode("utf-8"))
        time.sleep(0.001)

    # removing driver
    def _remove_driver(self):
        cmd = "sudo rmmod DRV_802154"
        print("")
        print(cmd)
        ret = subprocess.check_output(cmd.split(" "))
        time.sleep(0.001)        

        cmd = "tail -n 1 /var/log/messages"
        ret = subprocess.check_output(cmd.split(" "))
        print(ret.decode("utf-8"))
        time.sleep(0.001)

    # open driver
    def _open_driver(self):
        drv_path="/dev/bp3596"
        self.fpr=open(drv_path,"br+",buffering=0)
        self.start_flag = True
        thread.start_new_thread(self._loop,())
    
    # close driver
    def _close_driver(self):
        self.fpr.close()

        
