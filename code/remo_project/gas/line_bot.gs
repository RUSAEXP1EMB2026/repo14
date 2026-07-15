const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID';
const LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_LINE_CHANNEL_ACCESS_TOKEN';

function doPost(e) {
  const body = JSON.parse(e.postData.contents);
  const events = body.events || [];

  events.forEach(function(event) {
    if (event.type !== 'message' || event.message.type !== 'text') {
      return;
    }

    const text = event.message.text;
    const settings = parseSettings(text);

    if (settings.length > 0) {
      saveSettings(settings);
      reply(event.replyToken, '設定完了しました');
    } else {
      reply(event.replyToken, '時刻を読み取れませんでした。例: 起床 07:00 帰宅 18:30 就寝 23:00');
    }
  });

  return ContentService.createTextOutput('ok');
}

function parseSettings(text) {
  const pairs = [
    ['wake_time', /起床s*([0-2]?d:[0-5]d)/],
    ['return_time', /帰宅s*([0-2]?d:[0-5]d)/],
    ['sleep_time', /就寝s*([0-2]?d:[0-5]d)/],
  ];

  return pairs
    .map(function(pair) {
      const match = text.match(pair[1]);
      return match ? [pair[0], match[1]] : null;
    })
    .filter(Boolean);
}

function saveSettings(settings) {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName('Settings');
  const values = sheet.getDataRange().getValues();
  const keyToRow = {};

  for (let i = 1; i < values.length; i++) {
    keyToRow[values[i][0]] = i + 1;
  }

  settings.forEach(function(setting) {
    const key = setting[0];
    const value = setting[1];
    if (keyToRow[key]) {
      sheet.getRange(keyToRow[key], 2).setValue(value);
    } else {
      sheet.appendRow([key, value]);
    }
  });
}

function reply(replyToken, message) {
  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN,
    },
    payload: JSON.stringify({
      replyToken: replyToken,
      messages: [{ type: 'text', text: message }],
    }),
  });
}
