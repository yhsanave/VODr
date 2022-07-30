# VOD Uploader

Simple tool for uploading tournament vods to YouTube using the [start.gg](https://start.gg) API for set data. I designed this tool to work with vods recorded using the [AverMedia Live Gamer Portable 2 Plus](https://www.avermedia.com/us/product-detail/GC513), since I bring a few to tournaments I go to and there isn't a way to have it label the vods, but it should work with any vods (though if you're uploading stream vods there are better tools out there for managing that process, such as [Streameta](https://streameta.com/)).

# Title/Description Templates

VOD Uploader allows you to customize the titles and descriptions of your videos with dynamic templates. You can edit the templates using the following files:

- Title: `/templates/title.txt`
- Description: `/templates/description.txt`

Note that YouTube only allows titles up to 100 characters long. Titles can get very long when expanding template strings, particularly if a player played many different characters, so I recommend using `%TournamentShort` and `%RoundShort` for titles to avoid exceeding this limit.

## Template Syntax

|      Argument      |            Description             |                      Example                      |
| :----------------: | :--------------------------------: | :-----------------------------------------------: |
|   `%Tournament`    |        Full tournament name        |               Local of Lafayette 69               |
| `%TournamentShort` |    Abbreviated tournament name     |                      LoL#69                       |
|      `%Link`       | Link to the tournament on start.gg | https://start.gg/tournament/local-of-lafayette-69 |
|      `%Event`      |         Name of the event          |                      Singles                      |
|      `%Phase`      |         Name of the phase          |                       Pools                       |
|      `%Round`      |          Full round name           |                  Winners Round 1                  |
|   `%RoundShort`    |       Abbreviated round name       |                        WR1                        |
|       `%P1`        |   Player 1 tag (includes prefix)   |               puff.rest \| Yhsanave               |
|       `%P2`        |   Player 2 tag (includes prefix)   |                   Not Yhsanave                    |
|     `%P1Chars`     |      Characters for player 1       |                    Jigglypuff                     |
|     `%P2Chars`     |      Characters for player 2       |                Sonic, Yoshi, Steve                |

## Example Templates

Template:

> %TournamentShort %Event %Pools %RoundShort - %P1 (%P1Chars) vs %P2 (%P2Chars)

Output:

>  LoL#69 Singles Pools WR1 - puff.rest | Yhsanave (Jigglypuff) vs Not Yhsanave (Sonic, Yoshi, Steve)

---

Template:

> %P1 vs %P2 at %Tournament in %Round
> 
> Bracket: %Link 
>
> This is the bit of the description where I would include other information or link to my other socials, but since this is just an example to demonstrate how one would put this part in the description I won't actually put anything meaningfull here. You can put any text in these templates, only the special strings listed above will be dynamically replaced.

Output: 

> puff.rest | Yhsanave vs Not Yhsanave at Local of Lafayette 69 in Winners Round 1
> 
> Bracket: https://start.gg/tournament/local-of-lafayette-69
>
> This is the bit of the description where I would include other information or link to my other socials, but since this is just an example to demonstrate how one would put this part in the description I won't actually put anything meaningfull here. You can put any text in these templates, only the special strings listed above will be dynamically replaced.
