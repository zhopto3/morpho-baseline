#!/bin/bash

base=../../output

lem=../../../lemmatizer/reformat_dicts/lemmas
voc=../../../lemmatizer/reformat_dicts/in_voc

mkdir -p $base

for var in rm-sursilv rm-sutsilv rm-surmiran rm-puter rm-vallader rm-rumgr
do
    mkdir -p ${base}/${var}

    for pos in verb adj noun other
    do
        echo "Now on ${var} ${pos}"
        mkdir -p ${base}/${var}/${pos}

        #1. collect plausible pairs of words based on the longest common string between lemmas and types
        python3 ./make_plausible_pairs.py --text ${voc}/${var}.txt --lemmas ${lem}/${var}_${pos}.txt --output ${base}/${var}/${pos}/pairs.txt

        #2. find frequent rules for converting between lemma and types in vocab
        python3 ./compute_edittrees.py --pairs ${base}/${var}/${pos}/pairs.txt --output ${base}/${var}/${pos}/et.txt --lemmatizer

        #3. Complete paradigms based on the edit trees
        python3 ./predict_by_edittrees.py --et ${base}/${var}/${pos}/et.txt --lemmas ${lem}/${var}_${pos}.txt --output ${base}/${var}/${pos}/pred.txt
    done
done