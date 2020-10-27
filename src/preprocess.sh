#!/usr/bin/env bash

sed -i 's/"wikipediaUrl": , //g' $1
jq '{url: .url, lang: .lang, date: .date, score: .score, magnitude: .magnitude, entities: [(.entities[] | select(.wikipediaUrl) | {name: .name, type: .type, numMentions: .numMentions, avgSalience: .avgSalience})]}' $1 | jq -s . > $2
