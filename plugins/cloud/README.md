# Plugin "Cloud"
With this plugin, the world of DCSServerBot gets even bigger!</br>
When using DCSServerBot in your Discord and with your DCS servers, people gather lots of statistics. As people often 
not only fly in one community, they might want to see their statistics that they gathered in all communities in a 
single place.</br>
That said, DCSServerBot offers the opportunity to use a cloud based database system, to upload aggregated statistics
for every active user into the cloud. Users then can use Discord commands to see their overall stats, like they are
used to see with .stats.

In the future it is planned to have "Cloud Campaigns" that span over multiple groups that want to participate and
compete against each other!

**__ATTENTION__**</br>
The Cloud statistics are meant for larger servers only. I am happy to provide you access to it, using a token, provided 
by me. The service comes free of charge but without any liabilities or guarantees, you can use it or leave it and so 
can I revoke any token at any time.

## Global Ban System
If you opt in to the cloud plugin and even have not opted in to the cloud statistics, you can still use the global ban
system. We've put together a group consisting of the admins of the most popular DCS servers and we monitor what's going
on in the community. When we see someone that is crashing servers by hacking or any other **really** (really) bad stuff,
we put them in the global ban list. Nobody that gets usually banned on a server for misbehaviour will get onto the list.
There are only the real bad guys on it.</br>
If you opt in to that plugin, you already participate from that ban list.</br>
If you are a server admin of a large server and not part of DGSA yet, send me a DM.

## Configuration
```json
{
  "configs": [
    {
      "protocol": "https",
      "host": "dcsserverbot-prod.herokuapp.com",
      "token": "<secret token>",                       -- You need to contact me for a token, if you want to use this service.
      "port": 443
    }
  ]
}
```

## Discord Commands
| Command               | Parameter        | Role      | Description                                          |
|-----------------------|------------------|-----------|------------------------------------------------------|
| .resync               | [@member / ucid] | DCS Admin | Resyncs all players (or this player) with the cloud. |
| .cloudstats / .cstats | [@member / ucid] | DCS       | Display player cloud statistics (overall, per guild) |
