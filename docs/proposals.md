
MEMC: What things we are trying to analysis?

1. what "factors" help deal making or "target" making? (we will work in this repo)
    1. features:
        1. avg_latency
        2. initial latency
        3. quality 
        4. who_reply
        5. day message throughput
        6. hour message throughput
        7. 10 min message throughput
        8. time (hour)
        9. time (day / week)
        ... others

    2. target:
        1. deal make or not
        2. initial latency

2. Which message can use AI to replace? ( hard to answer)
3. Other visualization (only need notebooks to conduct)
    1. y: message throughput (day), label the 明星 vs x: time
    2. initial latency vs deal makr or not



點客數 vs latency
Latency vs 成功率
單位訊息成本 vs ai 訊息成本
用這些指標設計我們的ai 模型
幾趴 可以自動回
幾趴一定要人為介入
明星label上去
做一個自動判斷能不能ai回的系統
Label成高機率客戶之後，開始人工回
每個小編登入自己的帳號 可以互相比對 分析該回答的內容
做覆盆檢討

#### Inpuy json format:
```json
{
  "participants": [
    {
      "name": "Aaron Chien"
    },
    {
      "name": ""
    }
  ],
  "messages": [
    {
      "sender_name": "",
      "timestamp_ms": 1740924995824,
      "content": "",
      "is_geoblocked_for_viewer": false,
      "is_unsent_image_by_messenger_kid_parent": false
    },
    {
      "sender_name": "",
      "timestamp_ms": 1738442381398,
      "content": "",
      "is_geoblocked_for_viewer": false,
      "is_unsent_image_by_messenger_kid_parent": false
    },
  ]
}
```


#### Output json format:
```json
{
  "features":{

  },
  "targets":{

  }
  "messages": [
    {
      "sender_name": "",
      "timestamp_ms": 1740924995824,
      "content": "",
    },
    {
      "sender_name": "",
      "timestamp_ms": 1738442381398,
      "content": "",
    },
  ]
}
```