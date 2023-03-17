*** Variables ***
${base_url}         http://server
${words}            life;universe;everything
${invalid_words}            some;invalid;words

*** Settings ***
Library    RequestsLibrary

Suite Setup     Create Session  sess    ${base_url}

*** Test Cases ***
Test Answer Resource For Success Case
    ${resp}=    GET On Session    sess    url=/answer?search=${words}   expected_status=200
    Should Be Equal As Integers     ${resp.status_code}     200     Http Status Code is not 200
    Should Be Equal     ${resp.text}     42     Http Response is not 42

Test Answer Resource For Not Found Case
    ${resp}=    GET On Session    sess    url=/answer?search=${invalid_words}   expected_status=404
    Should Be Equal As Integers     ${resp.status_code}     404     Http Status Code is not 404
    Should Be Equal     ${resp.text}     unknown     Http Response is not unknown

Test Answer Resource For Bad Request Case
    ${resp}=    GET On Session    sess    url=/answer   expected_status=400
    Should Be Equal As Integers     ${resp.status_code}     400     Http Status Code is not 400
    Should Be Equal     ${resp.text}     unknown     Http Response is not unknown