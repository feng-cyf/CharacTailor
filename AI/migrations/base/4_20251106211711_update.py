from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `personas` ADD `deploy_type` VARCHAR(20) NOT NULL DEFAULT 'cloud';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `personas` DROP COLUMN `deploy_type`;"""


MODELS_STATE = (
    "eJztXW1T2zgQ/itMPrUzXIempe3ctwTSa+6AdCDctWU6HmGLRFNbSm0FyHT47yf5VZYlEx"
    "PH2Km+MLGkta1HL7v77Fr86l2DAL46RsAlsyX8hAJK/FXvz71fPQw8yH6oG+zv9cBikVTz"
    "Swqu3bC9Eze15kLb64D6wKas/ga4AWRFDgxsHy0oIpiV4qXr8kJis4YIz7KiJUY/2c0omU"
    "E6hz6ruPrOihF24D0M+OVVbwH9gGBgIafH6q56ywD6/IK1C2AQsEeEVVxu8cO6QdB1cl1M"
    "XzmSCRtYdLUIK4/mwP8YivAXvLZs4i49rBBbrOicPSmRYx3hpTOIoQ8odIS+867FcCVFUT"
    "dZAfWXMO2fkxU48AYsXSpgtSaANsEcfIRpEHbaA/eWC/GMztnl64ODh6hbWaejZrwL/w7O"
    "jz4Nzl+wVi95Xwgbw2iQz+KqflT3EN4EUBDdJhyWDN5wODw2EGAGi/hO4T1V4yvL1QNwUp"
    "AhnE3JeiAuQXQ6+jLlL+0FwU9XBPLF6eBLiLG3imtOJmd/Jc0F4I9OJsMQb2GFEmr5MFiw"
    "t6iEryxn8FXjCz3CXxG41g2EzjWwfxRR/ugSoIFZLS6BfcPltwX3wavDraB9PLkcnoz2Pp"
    "+PjsYX48lZDt+oMtyDf7qIhr08Hw1OJHBtH/LeWlHv86AesxqKPKjGNS8p4enEoq+SH+2c"
    "yj3WB2eC3VW80ZdN7fHp6GI6OP2cm9/Hg+mI1/Tz2MelL95J+3Z6k73/xtNPe/xy79vkLB"
    "ymBQnozA+fmLWbfuvxdwJLSixM7izgCDopKU2AyQ2soJQr6NS8VFd2pLxSPVxHpx7qVeph"
    "rFEzLAUrpgKWealuYlmjgSIZJNWwFES6CWQ9k5Kb0Dc/lFZePNsUqpH4EM3wP3AVQjtmLw"
    "mwrbI4QlfjIrtP+zB9SOZFUppthj64S10LaemxHw50YaQDjwYXR4PjUa8wIzdG7jK+SXdh"
    "E1bZ45jFqmJj2D5n9+kucnm9mQPvnGny8/HRtBeuXm5/3gHfsXLLmNeQPpFK0rbFKq/vyS"
    "UAMz/NiXvysB+jO0qsXy23UGixrycXMlu6OXZBmJSCyRkSDYHNJkwJsaDSMWOs8ROU2oWP"
    "uDQx4+F/VhJhxp/yR//12/dvP7x59/YDaxK+SVryvkTbjM+mjzAGczb+CLM9tJKjlZMy/l"
    "WsloFTGUhBplkYX7cWRoBnSg2tBzGVMBAmEN4jSFcVQUxlmoWx31oYbeB6lVe0KNQskO9a"
    "CyS8t1mlB7GCeSqj83JizYL5prVgeoQ4FnsWxAGquMaLos2C+ra1oGbW7i1gjrytYPfX4p"
    "0F6WahPegAtMw5vEZu1UmrkW8W3vethdchHsIAU4sv7koxVVmwObath+GSIeT2no5qnnLr"
    "r0O59fWUW79AXLKnz5hVacFbpdbSh/oKgk+CNfYidzjUFzn0FeZrKtDgPLXn0abSIl5Ysb"
    "VaAVn6KpWlB7Mo2SCqwSpgZl2LcXWWrM9Khl1LKYkijxNLdUH5egM2pB5myYSXdz68bGJ4"
    "W4jhmTDUemGo5wiknDLt6KN4wHMBlLRmXx848cQ2jcVLwqeuoukRBkyQtyB+OHuswGbTys"
    "ROao+diJhX2BwlsW5ukPV7XOxxtKKvJYh0BcXmMyqvoeOwN7JuoU2JQucMEQb+SucmFKVl"
    "RbSi0V7XJY92yIESoWZID8dng/OvaqyT9qJlNfw6HQ0ktAubblHD64kulbCJrcok4h0zkO"
    "YV4wgKYQOs8dp22mtzQUAtYNswCKDCvisf24KwGd5nHd745YUIfzg2bMSWKotJa7zLYs0x"
    "VRvEp+omqjxIAbfpi7j9fTE509nsmYwE2iVm/blykE3391wU0O9dM4Z4r8vtTtnElKYzv4"
    "FsdxrSyJBGvxVplOQ2FzgjIelZRxnFKcVNUEY3S2wn4fQopZaTRZSUJte25wOjZr/ZrSuy"
    "pKeQEozC6ydgm8h1c8PcyidH4psVENVzSZKYidor6aRwo6gwT5P2Hc4t2cI3hgsI7bllM9"
    "TYRg99ZjQiW5FlqjdH9XcwxukaxmlBCVaY0SrZBmd3dNP6ZvdWtuCMcLtGoNLELkqaCb3G"
    "hDYs3k7QPEUWDwUW2+DRrWKLGhLiQoA1sQRRTvYCmeC2BjI1x2uP2EwmJ7kxG45lc+XydD"
    "hiW9XLPOdd5H8cuHBJ9bCtJNZkFqJLlk5tO349kdsCS6H3uYunPylUwjAW/fjPOXR1mXS6"
    "A7LatyXpqAyJxOUr1Iq/YN8IlE5+yl8kDBO31gu/L51tBAnnuWLu5TS6XcfQ2ZCrykOrgP"
    "IU4NWU8L9b5Q23TdmUsIYecaBr5di4pBc+nz3M7pGImAgm4ocI/4CrFL6YxUrRj+vyHBed"
    "+2Q5m+ums5awZOWWnDv1UMI1Jqu9wDUK24COaxR3m4bS06J8tNQiCS/tpe9DTC3xQEEt/9"
    "ieQ3l28MxA9gYYhi6thfANqeKtKUSNu7b/uLtmrPr6rXrjAu+oCxznorBpr/xydK1ElkzY"
    "DG+7Elkywi9M5r1XrN512EJB2GigNTSQwvyqYFmppRtkRJKfdRla9cd4TP6LyX9pxdl90l"
    "rdGL4tn+FXw9JeF0b1LpZD9GI03TsefRxcnpSe6WcYzvpoqxLaI1y5Bc4jWc86wiNlv7bM"
    "dsTArsdotEE97FouFQeoah6VKNNNpbuVAL5xpnfC29I400y5IEVu3BqedCpZw8A272TtzL"
    "gWvGhKKHOC+cluXMFxPrbqlyEld/gtPxLxYxstmKMF22xvoVsBTLVwg8fCtAfHxV21nPE7"
    "4//um8yKTZMJ5MPL0WbAqM5N7ygy4ukkT4VDPAWlozCYnJte4lKanJtt5Nzk8kk2SbvZgG"
    "9rV+aN0BE5+SZLUMpn3uSZOTn3RszLqSvzJvKYHuGgpBmuZKSKq6CMn1K9b7101VVKnidE"
    "8Hdtvs5+DnlzblTd50ahwBJY7mr5H4JggwkgVSegyQAxpJX5/4Zt8ShNXNrEpVsXl+5IPL"
    "oZ5EpC0M96qMUA+sie9woWblxeYtWCrMU2w67GNq3ZNr1lM1F5coJePwgi3dQP/cPDdT6J"
    "OzzUfxPH66T/wcUWRgUQ4+bdBHA7MWjdebCl3yNozoN9Shbo8+mLraaBVogv1K9YHv4HTR"
    "4MKg=="
)
