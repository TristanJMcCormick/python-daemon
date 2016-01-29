TASKS = [
    'FOURSQUARE',
]


SMS_TEMPLATES = {
    'WRONG_TASK_TYPE':'Something was wrong with the type of query. We can only handle ' + ' ,'.join(TASKS),
    'MALFORMED_QUERY':{
        'foursquare':'Something was wrong with the query. Does it have the form: foursquare <queryterm> [-n <cityname>]',
        },
    'NO_RESPONSE':{
        'foursquare':'No results for that venue'
    },
    'QUERY_RESPONSE':{
        'foursquare':'Bingo. {0}'
    },
    'ADMIN_NOTIFIED':'Something went wrong with foursquare integration. Tristan is checking into it!',
    'ADMIN_MESSAGE':'Foursquare api is down or something. Check credentials and API status',
}
