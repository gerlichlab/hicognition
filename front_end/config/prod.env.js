"use strict";

module.exports = {
    NODE_ENV: '"production"',
    API_URL: '"/flask/api/"',
    STATIC_URL: '"/static/"',
    VERSION: "0.6",
    NOTIFICATION_URL: '"/flask/stream"',
    ALLOW_PUBLIC_UPLOAD: process.env.ALLOW_PUBLIC_UPLOAD,
};
