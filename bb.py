[{'name': 'Contact', 'sql': 'CREATE TABLE Contact(UserName TEXT PRIMARY KEY ,Alias TEXT,EncryptUserName TEXT,DelFlag INTEGER DEFAULT 0,Type INTEGER DEFAULT 0,VerifyFlag INTEGER DEFAULT 0,Reserved1 INTEGER DEFAULT 0,Reserved2 INTEGER DEFAULT 0,Reserved3 TEXT,Reserved4 TEXT,Remark TEXT,NickName TEXT,LabelIDList TEXT,DomainList TEXT,ChatRoomType int,PYInitial TEXT,QuanPin TEXT,RemarkPYInitial TEXT,RemarkQuanPin TEXT,BigHeadImgUrl TEXT,SmallHeadImgUrl TEXT,HeadImgMd5 TEXT,ChatRoomNotify INTEGER DEFAULT 0,Reserved5 INTEGER DEFAULT 0,Reserved6 TEXT,Reserved7 TEXT,ExtraBuf BLOB,Reserved8 INTEGER DEFAULT 0,Reserved9 INTEGER DEFAULT 0,Reserved10 TEXT,Reserved11 TEXT)'}, {'name': 'OpLog', 'sql': 'CREATE TABLE OpLog(ID INTEGER PRIMARY KEY,CMDItemBuffer BLOB)'}, {'name': 'Session', 'sql': 'CREATE TABLE Session(strUsrName TEXT  PRIMARY KEY,nOrder INT DEFAULT 0,nUnReadCount INTEGER DEFAULT 0,parentRef TEXT,Reserved0 INTEGER DEFAULT 0,Reserved1 TEXT,strNickName TEXT,nStatus INTEGER,nIsSend INTEGER,strContent TEXT,nMsgTypeINTEGER,nMsgLocalID INTEGER,nMsgStatus INTEGER,nTime INTEGER,editContent TEXT,othersAtMe INT,Reserved2 INTEGER DEFAULT 0,Reserved3 TEXT,Reserved4 INTEGER DEFAULT 0,Reserved5 TEXT,bytesXml BLOB)'}, {'name': 'AppInfo', 'sql': 'CREATE TABLE AppInfo(InfoKey TEXT PRIMARY KEY,AppId TEXT,Version INT,IconUrl TEXT,StoreUrl TEXT,WatermarkUrl TEXT,HeadImgBuf BLOB,Name TEXT,Description TEXT,Name4EnUS TEXT,Description4EnUS TEXT,Name4ZhTW TEXT,Description4ZhTW TEXT)'}, {'name': 'ContactHeadImgUrl', 'sql': 'CREATE TABLE ContactHeadImgUrl(usrName TEXT PRIMARY KEY,smallHeadImgUrl TEXT,bigHeadImgUrl TEXT,headImgMd5 TEXT,reverse0 INT,reverse1 TEXT)'}, {'name': 'BizInfo', 'sql': 'CREATE TABLE BizInfo(UserName TEXT PRIMARY KEY,Type INTEGER DEFAULT 0,Belong TEXT,AcceptType INTEGER DEFAULT 0,Reserved1 INTEGER DEFAULT 0,Reserved2 TEXT,BrandList TEXT,BrandFlag INTEGER DEFAULT 0,BrandInfo TEXT,BrandIconURL TEXT,UpdateTime INTEGER DEFAULT 0,ExtInfo TEXT,Reserved3 INTEGER DEFAULT 0,Reserved4 TEXT,Reserved5 INTEGER DEFAULT 0,Reserved6 TEXT,Reserved7 INTEGER DEFAULT 0,Reserved8 TEXT,Reserved9 BLOB)'}, {'name': 'TicketInfo', 'sql': 'CREATE TABLE TicketInfo(UserName TEXT PRIMARY KEY,Ticket TEXT,Reserved1 INTEGER DEFAULT 0,Reserved2 TEXT,Reserved3 INTEGER DEFAULT 0,Reserved4 TEXT)'}, {'name': 'ChatRoom', 'sql': 'CREATE TABLE ChatRoom(ChatRoomName TEXT PRIMARY KEY,UserNameList TEXT,DisplayNameList TEXT,ChatRoomFlag int Default 0,Owner INTEGER DEFAULT 0,IsShowName INTEGER DEFAULT 0,SelfDisplayName TEXT,Reserved1 INTEGER DEFAULT 0,Reserved2 TEXT,Reserved3 INTEGER DEFAULT 0,Reserved4 TEXT,Reserved5 INTEGER DEFAULT 0,Reserved6 TEXT,RoomData BLOB,Reserved7 INTEGER DEFAULT 0,Reserved8 TEXT)'}, {'name': 'ChatRoomInfo', 'sql': 'CREATE TABLE ChatRoomInfo(ChatRoomName TEXT PRIMARY KEY,Announcement TEXT,InfoVersion INTEGER DEFAULT 0,AnnouncementEditor TEXT,AnnouncementPublishTime INTEGER DEFAULT 0,ChatRoomStatus INTEGER DEFAULT 0,Reserved1 INTEGER DEFAULT 0,Reserved2 TEXT,Reserved3 INTEGER DEFAULT 0,Reserved4 TEXT,Reserved5 INTEGER DEFAULT 0,Reserved6 TEXT,Reserved7 INTEGER DEFAULT 0,Reserved8 TEXT)'}, {'name': 'MainConfig', 'sql': 'CREATE TABLE MainConfig(Key TEXT PRIMARY KEY,Reserved0 INT,Buf BLOB,Reserved1 INT,Reserved2 TEXT)'}, {'name': 'RevokeMsgStorage', 'sql': 'CREATE TABLE RevokeMsgStorage (CreateTime INTEGER PRIMARY KEY,MsgSvrID INTERGER,RevokeSvrID INTERGER)'}, {'name': 'BizProfileV2', 'sql': 'CREATE TABLE BizProfileV2 (TalkerId INTEGER PRIMARY KEY, UserName TEXT, ServiceType INTEGER, ArticleCount INTEGER, FriendSubscribedCount INTEGER, IsSubscribed INTEGER, Offset TEXT, IsEnd INTEGER, TimeStamp INTEGER, Reserved1 INTEGER, Reserved2 INTEGER, Reserved3 TEXT, Reserved4 TEXT, RespData BLOB, Reserved5 BLOB)'}, {'name': 'BizName2ID', 'sql': 'CREATE TABLE BizName2ID(UsrName TEXT PRIMARY KEY)'}, {'name': 'BizProfileInfo', 'sql': 'CREATE TABLE BizProfileInfo (tableIndex INTEGER PRIMARY KEY,tableVersion INTERGER,tableDesc TEXT)'}, {'name': 'BizSessionNewFeeds', 'sql': 'CREATE TABLE BizSessionNewFeeds (TalkerId INTEGER PRIMARY KEY, BizName TEXT, Title TEXT, Desc TEXT, Type INTEGER, UnreadCount INTEGER, UpdateTime INTEGER, CreateTime INTEGER, BizAttrVersion INTEGER, Reserved1 INTEGER, Reserved2 INTEGER, Reserved3 TEXT, Reserved4 TEXT, Reserved5 BLOB)'}, {'name': 'ChatInfo', 'sql': 'CREATE TABLE ChatInfo (Username TEXT, LastReadedSvrId INTEGER, LastReadedCreateTime INTEGER, Reserved1 INTEGER, Reserved2 INTEGER, Reserved3 TEXT, Reserved4 TEXT, Reserved5 INTEGER, Reserved6 TEXT, Reserved7 BLOB)'}, {'name': 'ChatLiveInfo', 'sql': 'CREATE TABLE ChatLiveInfo (RoomName TEXT, LiveId INTEGER, LiveName TEXT, AnchorName TEXT, Reserved1 INTEGER, Reserved2 INTEGER, Reserved3 TEXT, Reserved4 TEXT, Reserved5 BLOB,  UNIQUE (RoomName , LiveId ))'}, {'name': 'PatInfo', 'sql': 'CREATE TABLE PatInfo (username TEXT UNIQUE  PRIMARY KEY , suffix TEXT, reserved1 INTEGER DEFAULT 0, reserved2 INTEGER DEFAULT 0, reserved3 INTEGER DEFAULT 0, reserved4 INTEGER DEFAULT 0, reserved5 TEXT, reserved6 TEXT, reserved7 TEXT, reserved8 TEXT, reserved9 TEXT)'}, {'name': 'FTSContactTrans', 'sql': 'CREATE TABLE FTSContactTrans (username TEXT,reserve1 INTEGER, reserve2 TEXT)'}, {'name': 'FTSChatroomTrans', 'sql': 'CREATE TABLE FTSChatroomTrans (username TEXT,groupUsername TEXT,displayName TEXT,nickname TEXT,operation INTEGER,reserve1 INTEGER, reserve2 TEXT)'}, {'name': 'ChatroomTool', 'sql': 'CREATE TABLE ChatroomTool (ChatroomUsername TEXT, RoomToolsBuffer BLOB, Reserved1 INTEGER, Reserved2 TEXT, Reserved3 INTEGER, Reserved4 TEXT, Reserved5 BLOB,  UNIQUE (ChatroomUsername ))'}, {'name': 'ContactLabel', 'sql': 'CREATE TABLE ContactLabel (LabelId INTEGER PRIMARY KEY, LabelName TEXT, Reserved1 INTEGER, Reserved2 INTEGER, Reserved3 TEXT, Reserved4 TEXT, RespData BLOB, Reserved5 BLOB)'}, {'name': 'TopStoryReddotInfo', 'sql': 'CREATE TABLE TopStoryReddotInfo (MsgId TEXT PRIMARY KEY, Discovery INTEGER, Entry INTEGER, IosCliVersion INTEGER, AndroidCliVersion INTEGER, H5Version INTEGER, ExpireTime INTEGER, ReddotType INTEGER, TimeStamp INTEGER, ExtInfo TEXT, Seq INTEGER, ReddotText TEXT, ReddotIcon TEXT, Clear INTEGER, Priority INTEGER, HasRead INTEGER, Reserved1 INTEGER, Reserved2 INTEGER, Reserved3 TEXT, Reserved4 TEXT, Reserved5 INTEGER, Reserved6 TEXT, Reserved7 BLOB)'}]


cite_text = '''<msg>
        <appmsg appid="" sdkver="0">
                <title>1</title>
                <des />
                <username />
                <action>view</action>
                <type>57</type>
                <showtype>0</showtype>
                <content />
                <url />
                <lowurl />
                <forwardflag>0</forwardflag>
                <dataurl />
                <lowdataurl />
                <contentattr>0</contentattr>
                <streamvideo>
                        <streamvideourl />
                        <streamvideototaltime>0</streamvideototaltime>
                        <streamvideotitle />
                        <streamvideowording />
                        <streamvideoweburl />
                        <streamvideothumburl />
                        <streamvideoaduxinfo />
                        <streamvideopublishid />
                </streamvideo>
                <canvasPageItem>
                        <canvasPageXml><![CDATA[]]></canvasPageXml>
                </canvasPageItem>
                <refermsg>
                        <type>1</type>
                        <svrid>1745786385220000720</svrid>
                        <fromusr>wxid_4avtkgf32hjn22</fromusr>
                        <chatusr>wxid_4avtkgf32hjn22</chatusr>
                        <displayname>to be legend</displayname>
                        <msgsource>&lt;msgsource&gt;
        &lt;signature&gt;V1_lxDBqVSk|v1_lxDBqVSk&lt;/signature&gt;
        &lt;tmp_node&gt;
                &lt;publisher-id&gt;&lt;/publisher-id&gt;
        &lt;/tmp_node&gt;
&lt;/msgsource&gt;
</msgsource>
                        <content>你好呀, kwq</content>
                        <strid />
                        <createtime>1741526180</createtime>
                </refermsg>
                <appattach>
                        <totallen>0</totallen>
                        <attachid />
                        <cdnattachurl />
                        <emoticonmd5></emoticonmd5>
                        <aeskey></aeskey>
                        <fileext />
                        <islargefilemsg>0</islargefilemsg>
                </appattach>
                <extinfo />
                <androidsource>0</androidsource>
                <thumburl />
                <mediatagname />
                <messageaction><![CDATA[]]></messageaction>
                <messageext><![CDATA[]]></messageext>
                <emoticongift>
                        <packageflag>0</packageflag>
                        <packageid />
                </emoticongift>
                <emoticonshared>
                        <packageflag>0</packageflag>
                        <packageid />
                </emoticonshared>
                <designershared>
                        <designeruin>0</designeruin>
                        <designername>null</designername>
                        <designerrediretcturl><![CDATA[null]]></designerrediretcturl>
                </designershared>
                <emotionpageshared>
                        <tid>0</tid>
                        <title>null</title>
                        <desc>null</desc>
                        <iconUrl><![CDATA[null]]></iconUrl>
                        <secondUrl>null</secondUrl>
                        <pageType>0</pageType>
                        <setKey>null</setKey>
                </emotionpageshared>
                <webviewshared>
                        <shareUrlOriginal />
                        <shareUrlOpen />
                        <jsAppId />
                        <publisherId />
                        <publisherReqId />
                </webviewshared>
                <template_id />
                <md5 />
                <websearch>
                        <rec_category>0</rec_category>
                        <channelId>0</channelId>
                </websearch>
                <weappinfo>
                        <username />
                        <appid />
                        <appservicetype>0</appservicetype>
                        <secflagforsinglepagemode>0</secflagforsinglepagemode>
                        <videopageinfo>
                                <thumbwidth>0</thumbwidth>
                                <thumbheight>0</thumbheight>
                                <fromopensdk>0</fromopensdk>
                        </videopageinfo>
                </weappinfo>
                <statextstr />
                <musicShareItem>
                        <musicDuration>0</musicDuration>
                </musicShareItem>
                <finderLiveProductShare>
                        <finderLiveID><![CDATA[]]></finderLiveID>
                        <finderUsername><![CDATA[]]></finderUsername>
                        <finderObjectID><![CDATA[]]></finderObjectID>
                        <finderNonceID><![CDATA[]]></finderNonceID>
                        <liveStatus><![CDATA[]]></liveStatus>
                        <appId><![CDATA[]]></appId>
                        <pagePath><![CDATA[]]></pagePath>
                        <productId><![CDATA[]]></productId>
                        <coverUrl><![CDATA[]]></coverUrl>
                        <productTitle><![CDATA[]]></productTitle>
                        <marketPrice><![CDATA[0]]></marketPrice>
                        <sellingPrice><![CDATA[0]]></sellingPrice>
                        <platformHeadImg><![CDATA[]]></platformHeadImg>
                        <platformName><![CDATA[]]></platformName>
                        <shopWindowId><![CDATA[]]></shopWindowId>
                        <flashSalePrice><![CDATA[0]]></flashSalePrice>
                        <flashSaleEndTime><![CDATA[0]]></flashSaleEndTime>
                        <ecSource><![CDATA[]]></ecSource>
                        <sellingPriceWording><![CDATA[]]></sellingPriceWording>
                        <platformIconURL><![CDATA[]]></platformIconURL>
                        <firstProductTagURL><![CDATA[]]></firstProductTagURL>
                        <firstProductTagAspectRatioString><![CDATA[0.0]]></firstProductTagAspectRatioString>
                        <secondProductTagURL><![CDATA[]]></secondProductTagURL>
                        <secondProductTagAspectRatioString><![CDATA[0.0]]></secondProductTagAspectRatioString>
                        <firstGuaranteeWording><![CDATA[]]></firstGuaranteeWording>
                        <secondGuaranteeWording><![CDATA[]]></secondGuaranteeWording>
                        <thirdGuaranteeWording><![CDATA[]]></thirdGuaranteeWording>
                        <isPriceBeginShow>false</isPriceBeginShow>
                        <lastGMsgID><![CDATA[]]></lastGMsgID>
                        <promoterKey><![CDATA[]]></promoterKey>
                        <discountWording><![CDATA[]]></discountWording>
                        <priceSuffixDescription><![CDATA[]]></priceSuffixDescription>
                        <showBoxItemStringList />
                </finderLiveProductShare>
                <finderOrder>
                        <appID><![CDATA[]]></appID>
                        <orderID><![CDATA[]]></orderID>
                        <path><![CDATA[]]></path>
                        <priceWording><![CDATA[]]></priceWording>
                        <stateWording><![CDATA[]]></stateWording>
                        <productImageURL><![CDATA[]]></productImageURL>
                        <products><![CDATA[]]></products>
                        <productsCount><![CDATA[0]]></productsCount>
                </finderOrder>
                <finderShopWindowShare>
                        <finderUsername><![CDATA[]]></finderUsername>
                        <avatar><![CDATA[]]></avatar>
                        <nickname><![CDATA[]]></nickname>
                        <commodityInStockCount><![CDATA[]]></commodityInStockCount>
                        <appId><![CDATA[]]></appId>
                        <path><![CDATA[]]></path>
                        <appUsername><![CDATA[]]></appUsername>
                        <query><![CDATA[]]></query>
                        <liteAppId><![CDATA[]]></liteAppId>
                        <liteAppPath><![CDATA[]]></liteAppPath>
                        <liteAppQuery><![CDATA[]]></liteAppQuery>
                        <platformTagURL><![CDATA[]]></platformTagURL>
                        <saleWording><![CDATA[]]></saleWording>
                        <lastGMsgID><![CDATA[]]></lastGMsgID>
                        <profileTypeWording><![CDATA[]]></profileTypeWording>
                        <reputationInfo>
                                <hasReputationInfo>0</hasReputationInfo>
                                <reputationScore>0</reputationScore>
                                <reputationWording />
                                <reputationTextColor />
                                <reputationLevelWording />
                                <reputationBackgroundColor />
                        </reputationInfo>
                        <productImageURLList />
                </finderShopWindowShare>
                <findernamecard>
                        <username />
                        <avatar><![CDATA[]]></avatar>
                        <nickname />
                        <auth_job />
                        <auth_icon>0</auth_icon>
                        <auth_icon_url />
                        <ecSource><![CDATA[]]></ecSource>
                        <lastGMsgID><![CDATA[]]></lastGMsgID>
                </findernamecard>
                <finderGuarantee>
                        <scene><![CDATA[0]]></scene>
                </finderGuarantee>
                <directshare>0</directshare>
                <gamecenter>
                        <namecard>
                                <iconUrl />
                                <name />
                                <desc />
                                <tail />
                                <jumpUrl />
                        </namecard>
                </gamecenter>
                <patMsg>
                        <chatUser />
                        <records>
                                <recordNum>0</recordNum>
                        </records>
                </patMsg>
                <secretmsg>
                        <issecretmsg>0</issecretmsg>
                </secretmsg>
                <referfromscene>0</referfromscene>
                <gameshare>
                        <liteappext>
                                <liteappbizdata />
                                <priority>0</priority>
                        </liteappext>
                        <appbrandext>
                                <litegameinfo />
                                <priority>-1</priority>
                        </appbrandext>
                        <gameshareid />
                        <sharedata />
                        <isvideo>0</isvideo>
                        <duration>-1</duration>
                        <isexposed>0</isexposed>
                        <readtext />
                </gameshare>
                <mpsharetrace>
                        <hasfinderelement>0</hasfinderelement>
                        <lastgmsgid />
                </mpsharetrace>
                <wxgamecard>
                        <framesetname />
                        <mbcarddata />
                        <minpkgversion />
                        <mbcardheight>0</mbcardheight>
                        <isoldversion>0</isoldversion>
                </wxgamecard>
        </appmsg>
        <fromusername>wxid_e3p1sq5livwb32</fromusername>
        <scene>0</scene>
        <appinfo>
                <version>1</version>
                <appname />
        </appinfo>
        <commenturl />
</msg>
'''

img_cite = '''<msg>
        <appmsg appid="" sdkver="0">
                <title>1</title>
                <des />
                <username />
                <action>view</action>
                <type>57</type>
                <showtype>0</showtype>
                <content />
                <url />
                <lowurl />
                <forwardflag>0</forwardflag>
                <dataurl />
                <lowdataurl />
                <contentattr>0</contentattr>
                <streamvideo>
                        <streamvideourl />
                        <streamvideototaltime>0</streamvideototaltime>
                        <streamvideotitle />
                        <streamvideowording />
                        <streamvideoweburl />
                        <streamvideothumburl />
                        <streamvideoaduxinfo />
                        <streamvideopublishid />
                </streamvideo>
                <canvasPageItem>
                        <canvasPageXml><![CDATA[]]></canvasPageXml>
                </canvasPageItem>
                <refermsg>
                        <type>3</type>
                        <svrid>8264497157897535519</svrid>
                        <fromusr>47511800436@chatroom</fromusr>
                        <chatusr>wxid_e3p1sq5livwb32</chatusr>
                        <displayname>kwq</displayname>
                        <msgsource>&lt;msgsource&gt;&lt;sec_msg_node&gt;&lt;uuid&gt;2be67c20db6fc8684ce4c2bea57c709b_&lt;/uuid&gt;&lt;/sec_msg_node&gt;&lt;/msgsource&gt;</msgsource>
                        <content />
                        <strid />
                        <createtime>1741511191</createtime>
                </refermsg>
                <appattach>
                        <totallen>0</totallen>
                        <attachid />
                        <cdnattachurl />
                        <emoticonmd5></emoticonmd5>
                        <aeskey></aeskey>
                        <fileext />
                        <islargefilemsg>0</islargefilemsg>
                </appattach>
                <extinfo />
                <androidsource>0</androidsource>
                <thumburl />
                <mediatagname />
                <messageaction><![CDATA[]]></messageaction>
                <messageext><![CDATA[]]></messageext>
                <emoticongift>
                        <packageflag>0</packageflag>
                        <packageid />
                </emoticongift>
                <emoticonshared>
                        <packageflag>0</packageflag>
                        <packageid />
                </emoticonshared>
                <designershared>
                        <designeruin>0</designeruin>
                        <designername>null</designername>
                        <designerrediretcturl><![CDATA[null]]></designerrediretcturl>
                </designershared>
                <emotionpageshared>
                        <tid>0</tid>
                        <title>null</title>
                        <desc>null</desc>
                        <iconUrl><![CDATA[null]]></iconUrl>
                        <secondUrl>null</secondUrl>
                        <pageType>0</pageType>
                        <setKey>null</setKey>
                </emotionpageshared>
                <webviewshared>
                        <shareUrlOriginal />
                        <shareUrlOpen />
                        <jsAppId />
                        <publisherId />
                        <publisherReqId />
                </webviewshared>
                <template_id />
                <md5 />
                <websearch>
                        <rec_category>0</rec_category>
                        <channelId>0</channelId>
                </websearch>
                <weappinfo>
                        <username />
                        <appid />
                        <appservicetype>0</appservicetype>
                        <secflagforsinglepagemode>0</secflagforsinglepagemode>
                        <videopageinfo>
                                <thumbwidth>0</thumbwidth>
                                <thumbheight>0</thumbheight>
                                <fromopensdk>0</fromopensdk>
                        </videopageinfo>
                </weappinfo>
                <statextstr />
                <musicShareItem>
                        <musicDuration>0</musicDuration>
                </musicShareItem>
                <finderLiveProductShare>
                        <finderLiveID><![CDATA[]]></finderLiveID>
                        <finderUsername><![CDATA[]]></finderUsername>
                        <finderObjectID><![CDATA[]]></finderObjectID>
                        <finderNonceID><![CDATA[]]></finderNonceID>
                        <liveStatus><![CDATA[]]></liveStatus>
                        <appId><![CDATA[]]></appId>
                        <pagePath><![CDATA[]]></pagePath>
                        <productId><![CDATA[]]></productId>
                        <coverUrl><![CDATA[]]></coverUrl>
                        <productTitle><![CDATA[]]></productTitle>
                        <marketPrice><![CDATA[0]]></marketPrice>
                        <sellingPrice><![CDATA[0]]></sellingPrice>
                        <platformHeadImg><![CDATA[]]></platformHeadImg>
                        <platformName><![CDATA[]]></platformName>
                        <shopWindowId><![CDATA[]]></shopWindowId>
                        <flashSalePrice><![CDATA[0]]></flashSalePrice>
                        <flashSaleEndTime><![CDATA[0]]></flashSaleEndTime>
                        <ecSource><![CDATA[]]></ecSource>
                        <sellingPriceWording><![CDATA[]]></sellingPriceWording>
                        <platformIconURL><![CDATA[]]></platformIconURL>
                        <firstProductTagURL><![CDATA[]]></firstProductTagURL>
                        <firstProductTagAspectRatioString><![CDATA[0.0]]></firstProductTagAspectRatioString>
                        <secondProductTagURL><![CDATA[]]></secondProductTagURL>
                        <secondProductTagAspectRatioString><![CDATA[0.0]]></secondProductTagAspectRatioString>
                        <firstGuaranteeWording><![CDATA[]]></firstGuaranteeWording>
                        <secondGuaranteeWording><![CDATA[]]></secondGuaranteeWording>
                        <thirdGuaranteeWording><![CDATA[]]></thirdGuaranteeWording>
                        <isPriceBeginShow>false</isPriceBeginShow>
                        <lastGMsgID><![CDATA[]]></lastGMsgID>
                        <promoterKey><![CDATA[]]></promoterKey>
                        <discountWording><![CDATA[]]></discountWording>
                        <priceSuffixDescription><![CDATA[]]></priceSuffixDescription>
                        <showBoxItemStringList />
                </finderLiveProductShare>
                <finderOrder>
                        <appID><![CDATA[]]></appID>
                        <orderID><![CDATA[]]></orderID>
                        <path><![CDATA[]]></path>
                        <priceWording><![CDATA[]]></priceWording>
                        <stateWording><![CDATA[]]></stateWording>
                        <productImageURL><![CDATA[]]></productImageURL>
                        <products><![CDATA[]]></products>
                        <productsCount><![CDATA[0]]></productsCount>
                </finderOrder>
                <finderShopWindowShare>
                        <finderUsername><![CDATA[]]></finderUsername>
                        <avatar><![CDATA[]]></avatar>
                        <nickname><![CDATA[]]></nickname>
                        <commodityInStockCount><![CDATA[]]></commodityInStockCount>
                        <appId><![CDATA[]]></appId>
                        <path><![CDATA[]]></path>
                        <appUsername><![CDATA[]]></appUsername>
                        <query><![CDATA[]]></query>
                        <liteAppId><![CDATA[]]></liteAppId>
                        <liteAppPath><![CDATA[]]></liteAppPath>
                        <liteAppQuery><![CDATA[]]></liteAppQuery>
                        <platformTagURL><![CDATA[]]></platformTagURL>
                        <saleWording><![CDATA[]]></saleWording>
                        <lastGMsgID><![CDATA[]]></lastGMsgID>
                        <profileTypeWording><![CDATA[]]></profileTypeWording>
                        <reputationInfo>
                                <hasReputationInfo>0</hasReputationInfo>
                                <reputationScore>0</reputationScore>
                                <reputationWording />
                                <reputationTextColor />
                                <reputationLevelWording />
                                <reputationBackgroundColor />
                        </reputationInfo>
                        <productImageURLList />
                </finderShopWindowShare>
                <findernamecard>
                        <username />
                        <avatar><![CDATA[]]></avatar>
                        <nickname />
                        <auth_job />
                        <auth_icon>0</auth_icon>
                        <auth_icon_url />
                        <ecSource><![CDATA[]]></ecSource>
                        <lastGMsgID><![CDATA[]]></lastGMsgID>
                </findernamecard>
                <finderGuarantee>
                        <scene><![CDATA[0]]></scene>
                </finderGuarantee>
                <directshare>0</directshare>
                <gamecenter>
                        <namecard>
                                <iconUrl />
                                <name />
                                <desc />
                                <tail />
                                <jumpUrl />
                        </namecard>
                </gamecenter>
                <patMsg>
                        <chatUser />
                        <records>
                                <recordNum>0</recordNum>
                        </records>
                </patMsg>
                <secretmsg>
                        <issecretmsg>0</issecretmsg>
                </secretmsg>
                <referfromscene>0</referfromscene>
                <gameshare>
                        <liteappext>
                                <liteappbizdata />
                                <priority>0</priority>
                        </liteappext>
                        <appbrandext>
                                <litegameinfo />
                                <priority>-1</priority>
                        </appbrandext>
                        <gameshareid />
                        <sharedata />
                        <isvideo>0</isvideo>
                        <duration>-1</duration>
                        <isexposed>0</isexposed>
                        <readtext />
                </gameshare>
                <mpsharetrace>
                        <hasfinderelement>0</hasfinderelement>
                        <lastgmsgid />
                </mpsharetrace>
                <wxgamecard>
                        <framesetname />
                        <mbcarddata />
                        <minpkgversion />
                        <mbcardheight>0</mbcardheight>
                        <isoldversion>0</isoldversion>
                </wxgamecard>
        </appmsg>
        <fromusername>wxid_e3p1sq5livwb32</fromusername>
        <scene>0</scene>
        <appinfo>
                <version>1</version>
                <appname />
        </appinfo>
        <commenturl />
</msg>'''