---
title: "Session"
date: 2022-02-21T10:29:41+01:00
draft: true
---

HiCognition sessions encapsulate a particular configuration of widgets inside all open widgets.

## Creating a session

To save the current state of all your widget collections, click on `Save Session` in the top right menu:

<img src="/docs/save_session_menu.png" class="half-width">

This will open a dialogue, which allows you to name your current session:

<img src="/docs/save_session_dialogue.png" class="quarter-width">

When you click submit, this will persist your session in the database.

## Restoring sessions

After you created a session, you can restore your session, by clicking on the `My Session` button in the top right menu. This will open a dialogue that shows all your available sessions. Here, you can click on a particular session, which then shows the context options. Amongst these, you can click on `Restore`, which will restore the saved session.

<img src="/docs/session_table_with_context.png" class="half-width">

{{% notice warning %}}
Restoring a session with delete your current workspace configuration!
{{% /notice %}}

## Sharing a session with others

To share a session with other users of HiCognition, you can click on `Get Url` in the session table. This will show a url with a unique token for this session:

<img src="/docs/session_w_token.png" class="half-width">

When a user of HiCognition visits this url, the session will be automatically restored.

{{% notice warning %}}
If you share a particular dataset using a session, other users will have access to it!
{{% /notice %}}
