
#  simple framework to test IMS stack
tmtcUnitTest is a simple framework to do CI in IMS stack.
[SIPp](http://sipp.sourceforge.net/) is used to unit test various VoIP scenarioes.
Running logs are collected to check test result and generate reports. 
**Similar to Spirent Instrument's IMS test Module~~**
## design
- IMS stack process called **tmtclient**  is running on an Android phone
- **tmtclient** listens on port 21904 to recv cmd
- control process send cmd like Register, Call, Answer to control tmtclient
- SIPp serves as IMS Server to interact with **tmtclient**
Overall  Architecture 
![tmtc_arch](/sample/tmtc_ut_framework.png)
## Key Feature
- various IMS scenarioes with different Gateway are defined in SIPp xmls 
	- all base xmls are located in [bricks](/cases/bricks)
- case can be easily added by json format config
	-  sample case definition  refer to [reg](cases/reg) 
```
{  
  "description": {  
      "scenario"  : "reg",  
      "bugid"  : "123456",  
      "commitid"  : "abcdefg",  
      "category"  : "Registration",  
      "casename"  : "reg"  
  },  
  "ue": {  
      "tmtcport"  : 21904,  
      "execdir"  : "/data/data/ut/",  
      "config"  : "provision.ini",  
      "binary"  : "tmtclient",  
      "startuptime": 3,  
      "lib"  : [  
                  "libavatar_ut.so",  
                  "liblemon_ut.so"  
  ]   
  },    
  "cases": [  
    {  
      "desc": "Register",  
      "xml": "reg.xml",  
      "timeout": 2,  
      "tmtccmd": "c-reg"  
  
  },  
    {  
      "desc": "Subscribe/Notify",  
      "xml": "subs_notify.xml",  
      "timeout": 2,  
      "tmtccmd":  ""  
  }  
  ]    
}
```
- cases/subcases runtime and result are displayed in html by [Jinja2](http://jinja.pocoo.org/)
report sample
![report](/sample/tmtc_report.png)

## TODOs
- sdp parser
- platformization
	-  web UI based trigged to generate/run cases
	- record cases in DB



