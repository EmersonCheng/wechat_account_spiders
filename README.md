# wechat_account_spiders
wechat account spiders by python

Command help:

    options:
        --start                     start download
        --non-headless              start broswer without headless mode
        --disable-gpu               start broswer disable gpu
        --download-all-article      download all account articles
                                    instead of download latest day
    configure:
        --download-path             show download path
        --set-download-path         set download path
        --account-list              show account list
        --set-account               set account list
        --chromedriver-path         show chromedriver path
        --set-chromedriver-path     set chromedriver path
        -h, --help                  show help
    set account list:
        divide accounts name/id by ',' if you want download more than
        two account
            example:
                --set-account="midifan,python"
    