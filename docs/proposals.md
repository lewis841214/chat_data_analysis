
## MEMC: What things we are trying to analysis?

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
        3. user_reply_len>5 (to track whether the user will reply > 5 messages according to initial reply)

2. Which message can use AI to replace? ( hard to answer)
3. Other visualization (only need notebooks to conduct)
    1. y: message throughput (day), label the 明星 vs x: time
    2. initial latency vs deal makr or not


## implmentation steps
1. facebook data preprocessing ( get assistant, user, formated timestamp)
2. auto-reply filtering
3. processing the "features" and the "targets"
4. Draw graph according to feature vs target

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
  "conversation": [
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


#### formated json format:
```json
{
  "features":{

  },
  "targets":{

  }
  "conversation": [
    {
      "sender_name": "user",
      "timestamp_ms": 2025-03-04T02:48:53.016000,
      "content": "Hello",
    },
    {
      "sender_name": "Assistant",
      "timestamp_ms": 2025-03-04T02:48:53.016000,
      "content": "what can I help you?",
    },
  ]
}
```

