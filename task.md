

1. tool update
1.0 
```
    public static class S2bType {      
       public static final int NORMAL = 1;
       public static final int SOS    = 2;
       public static final int UT     = 4;
       public static final int MMS    = 8;
  }
```
   [Adapter]VoWifiSecurityManager: Start the s2b attach. type: 1, subId: 2
    C:\Users\Zhihua.Ye\Documents\MyJabberFiles\cindy.xie@spreadtrum.com
    0703-EE-MMS-Send-Receive.rar
1.1 [811623](http://bugzilla.spreadtrum.com/bugzilla/show_bug.cgi?id=811623)  ip changed.
1.2 ipsec related
1.3 ho procesdure, call steps
1.4 use service instead of adapter
01-16 23:01:43.589   911   911 I [Adapter]ImsCallSessionImpl: Accept an incoming call with call type is 2
01-16 23:01:43.591  1244  1926 I [VoWifiService]CallService: Answer the call, sessionId: 3, cookie: null, needAudio: true, needVideo: false
1.5 integrate ipsec
1.6 single video
1.7 [823352](http://bugzilla.spreadtrum.com/bugzilla/show_bug.cgi?id=823352) tcp data is fragmented , parser logic should be changed.
            183 Session Progress
            recv tcp data(len:1096) from [10.77.25.36:7777].  recv tcp data(len:169) from [10.77.25.36:7777].
-----------------------------------------------------
2. env setup
2.1 [x][prio_1], add filecmp logic to check binary config
2.2 [][prio_4], add delta logic to change provision.ini
    add config options in config.json
3. case category: reg, sip, sdp
3.1 tag, db support
4. log check, adb logcat -b main 
4.1 Tmtc_MtcCbSessCallIn check
5. sip/sdp parse
6. report gen
7. case gen
7.1 pause to emulate UE retransmit
7.2 just resend in sipp xml
