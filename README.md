# extract-keyword-tools

一、该项目主要功能是：处理文本数据根据关键词以及行号范围提取数据并将结果存储于xml文件，待处理的文件需要满足待处理的行数据的关键数据之间以逗号分隔，目前只兼容逗号
用户可以查看该项目提供的样本文本数据，如OsInfo.txt内容如下：
------------------------------------------------------------
Intel(R) System Scope Tool
Version: 3.0.1042
Build Date: Dec 28 2016
Copyright (C) Intel Corporation 2016
For any queries or issue contact: systemscopetool@intel.com
------------------------------------------------------------

OS Details
"Build Number", "9600"
"Build Type", "Multiprocessor Free"
"Caption", "Microsoft Windows Server 2012 R2 Datacenter"
"Code Set", "1252"
"Country Code", "1"
"Current Time Zone", "GMT  -8:0"
"Encryption Level", "256"
"Install Date", "23/12/2016"
"Locale", "0409"
"Manufacturer", "Microsoft Corporation"
"Number Of Users", "3"
"Organization", "Not Available"
"OS Architecture", "64-bit"
"OS Language", "English - United States"
"OS SKU", "Server Datacenter (full installation)"
"OS Type", "WINNT"
"Primary OS", "TRUE"
"Registered User", "Windows User"
"Serial Number", "00260-00000-09041-AA112"
"Service Pack Version", "Not Available"
"Status", "OK"
"System Directory", "C:\windows\system32"
"System Drive", "C:"
"Version", "6.3.9600"
"WIMBoot Configuration", "Not Enabled"
"Windows Directory", "C:\windows"
"WQL", "Unknown"

注意：这里的逗号分隔的行数据是我们处理的目标数据，所以如果你想用这个脚本，那么你的数据模式就应该像OsInfo.txt文本这样


二、以下提供一些使用本项目脚本的部分样例
    1、$ python extract_keyword_tools.py --help
    ************************************** 用法举例：*************************************

    ****  python extract_keyword_tools.py -f filename or --file=filename                   ****
    ****  python extract_keyword_tools.py --help                                           ****
    ****  python extract_keyword_tools.py -f filename -r range_line or --range=range_line  ****
    ****  python extract_keyword_tools.py -f filename -k keywords or --keyword=keywords    ****
    ****  python extract_keyword_tools.py -f filename -k keywords  --print                 ****

    ************************************** 用法举例：*************************************

    备注：--help参数 提供帮助选项 也可以用-help代替


    2、$ python extract_keyword_tools.py -f SMBIOS.txt -r '1,20' --print
    SMBIOS.txt
    BIOS Vendor      Intel Corporation
    BIOS Version     PLYXCRB1.86B.1001.D66.1701302155
    Starting Address Segment         F000h
    BIOS Release Date        01/30/2017
    BIOS ROM Size    16384 KB
    BIOS Characteristics Not Supported       No
    ISA is supported         No
    MCA is supported         No
    EISA is supported        No
    actual_file_name:       SMBIOS.txt
    result_file_list:       ['C:\\Users\\Public\\extract-keyword-tools\\result_text\\result_SMBIOS.txt']
    tab_num_file_list:      ['C:\\Users\\Public\\extract-keyword-tools\\result_text\\tab_num_dir\\tab_num_SMBIOS.txt']

    备注：-f 用于指定待处理的文本文件， -r 用于指定处理的行数范围 --print参数 功能是将结果数据显示在终端
    其中 -f filename 等价于 --file=filename 这里的文件支持绝对路径和相对路径，支持多个文件处理 多个文件时用法： -f 'file1;file2;.....'
         file1,file2,.....之间以分号分隔，并且-f后文件要用引号这个要注意
         -r range_line 等价于 --range=range_line


    3、$ python extract_keyword_tools.py -f SMBIOS.txt -k 'BIOS' --print
    SMBIOS.txt
    BIOS Vendor      Intel Corporation
    BIOS Version     PLYXCRB1.86B.1001.D66.1701302155
    BIOS Release Date        01/30/2017
    BIOS ROM Size    16384 KB
    BIOS Characteristics Not Supported       No
    BIOS is Upgradeable (Flash)      Yes
    BIOS shadowing is allowed        Yes
    BIOS ROM is socketed     No
    BIOS Boot Specification supported        Yes
    System BIOS Minor Release        0
    System BIOS Major Release        0
    actual_file_name:       SMBIOS.txt
    result_file_list:       ['C:\\Users\\Public\\extract-keyword-tools\\result_text\\result_SMBIOS.txt']
    tab_num_file_list:      ['C:\\Users\\Public\\extract-keyword-tools\\result_text\\tab_num_dir\\tab_num_SMBIOS.txt']

    备注：-k 参数用于指定提取的关键词，-k keywords 等价于--keyword=keywords

[extract-keyword-tools](https://github.com/MrFiona/extract-keyword-tools/wiki/_Footer/_edit)
    4、$ python extract_keyword_tools.py -f OsInfo.txt -k 'OS'  --print --combine
    OsInfo.txt
    OS Architecture          64-bit
    OS Language      English - United States
    OS SKU   Server Datacenter (full installation)
    OS Type          WINNT
    Primary OS       TRUE
    actual_file_name:       OsInfo.txt
    result_file_list:       ['C:\\Users\\Public\\extract-keyword-tools\\result_text\\result_OsInfo.txt']
    tab_num_file_list:      ['C:\\Users\\Public\\extract-keyword-tools\\result_text\\tab_num_dir\\tab_num_OsInfo.txt']

    备注：--combine 参数用于连接上次的结果，应用场景之一比如说，你本来想处理两个文件file1,file2，但是你第一次执行的时候只指定了一个文件file1
    这个时候你可以再次执行代码并且将文件file2作为待处理文件再加上--combine标记，当然你也可以把file1也带上，程序会自动识别并且覆盖上一次file1的处理；当然另一个应用
    场景就是你本来想处理file1文件的1，60行但是你第一次写成了1,45,不用担心只需要再次执行程序并且行号指定46，60再加上标记--combine即可当然你也可以重新执行不加标记的
    程序，行号指定1,60。

    注意：程序内部能够实现自动去重的功能，所以你并不需要担心你的结果会被重复记录


三、最终的输出结果请在result_text目录中查看，本项目的有些目录在实际的运行过程中会被删除，此处提供了这些多余的目录
脚本的第855行clear_temp_file函数用于清理一些目录，如果你想保留这些目录则只需将第855行语句注释即可


四、如果您想用这个项目作为您的日常工具，我会感到很荣幸，如果您能够提供一些建议那就更好了，由于这个代码只是简单用于日常处理
的脚本，仓促实现，未免出现很多不足甚至bug，也请各位看官多多提issue，我会第一时间查看并修复issue，再次感谢

