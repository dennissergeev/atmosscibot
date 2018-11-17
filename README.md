# AtmosSciBot
Twitter bot that generates word clouds of new open access publications in atmospheric sciences.

The bot parses RSS feeds of scientific journals, downloads new publications in HTML/XML and then builds a word cloud image of the extracted text.

https://twitter.com/AtmosSciBot

## On demand generation
A word cloud can be created if AtmosSciBot is mentioned in a tweet and **a URL to the HTML or XML page of an open-access publication** is included.
Note that the URL should directly lead to the page with the full text of the publication and **NOT** an abstract (so don't request EGU articles that are still in discussion state)!

The tweet has to contain a **short name** of the corresponding journal as a **hashtag**. Only the journals that are in the [list of journals](journal_list.json) are allowed: otherwise the bot would not know how to extract the text from HTML. The tweet also has to contain the following words in any order: "make", "word", "cloud", "please".

Example:
```
@AtmosSciBot make wordcloud please #JGRA http://onlinelibrary.wiley.com/doi/10.1002/2015JD024680/full
```

### Font selection
A on-demand generation request can contain a name of Google Font (https://fonts.google.com) and the wordcloud will use the chosen font if **the request is correct**.
To choose font, include `[font:<name of the font>]` in the tweet. The word cloud will use the "Regular" (400) style of the font.
This option is made possible thanks to this [google-font-download script](https://github.com/neverpanic/google-font-download).

Example:
```
@AtmosSciBot make wordcloud please [font:Raleway] #QJRMS https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/qj.2911
```
or (note the spaces)
```
@AtmosSciBot make wordcloud please [font:M PLUS 1p] #QJRMS https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/qj.2911
```
If something is wrong with the font-related request, the wordcloud is created using the default font (https://fonts.google.com/specimen/Chicle).


## Repo contents
* [Settings](settings-example.ini)
* [List of journals](journal_list.json)
* [License](LICENSE)
* [Main program](atmosscibot.py)

## Inspired by
* [Twitter Word Cloud Bot](https://github.com/defacto133/twitter-wordcloud-bot)
* [scireader](https://github.com/koldunovn/scireader)
