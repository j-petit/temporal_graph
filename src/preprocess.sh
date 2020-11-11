#!/usr/bin/env bash

sed -i 's/"wikipediaUrl": , //g' $1
if [ -z "$2" ]
then
    jq '{url: .url, lang: .lang, date: .date, score: .score, magnitude: .magnitude, entities: [(.entities[] | select(.["mid"]) | {name: .name, mid: .mid, type: .type, numMentions: .numMentions, avgSalience: .avgSalience})]}' $1 | jq -s .
else
    jq '{url: .url, lang: .lang, date: .date, score: .score, magnitude: .magnitude, entities: [(.entities[] | select(.["mid"]) | {name: .name, mid: .mid, type: .type, numMentions: .numMentions, avgSalience: .avgSalience})]}' $1 | jq -s . > $2
fi
