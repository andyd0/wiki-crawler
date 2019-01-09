# Wiki Crawler

Wiki Crawler will crawl Wikipedia starting from a random Wikipedia page (or specified page) and follow the first non-italicized link not surrounded by parentheses till it reaches `Philosophy` or fails to do so.

Options...

* When creating the `WikiCrawler` object, the following can be set...
  * Wiki page to start from. If `None`, then starts from a random page
  * Number of crawls
  * Ignoring invalid paths - Boolean that specifies whether the crawling should include invalid paths (dead ends, red links etc) into the count.
    * If this is to `False`, percentage of pages that lead to `Philosophy` will be shown.
  * Length of path - default is set to path lengths of 50 as just a hard limit but from testing rarely any path was any longer than around 25 page links
* "plot_distribution" method can be used to get a chart of the distribution of path lengths

## Implementation Details

Beautiful Soup was used to generate a parse HTML to process.

A logger is used to display summary details to screen so that there is a way to know at what point the processing is at. Full path details are saved to a log file as well.

### Details

* To avoid traversing to `Philosophy` down a known path, a `dictionary` with a wiki page as key and its distance from `Philosophy` as the value. When a new path is found, the dictionary is populated with the entire path and their distances from `Philosophy`. If an intersection is found, the traversing is terminated and the dictionary is populated with the new partial path while adjusting the distance based on what the distance of the intersection is from `Philosophy`. Since paths seem to usually end up down the same path, as the number of crawls increases, the number of intersections did tend to increase as well leading to improvements in processing time while avoiding unnecessary hits to Wikipedia.
* Cycles were handled similarly to valid paths to terminate cycle paths. But instead of a dictionary, two `sets` are used to keep track of a cycle
  * A local cycle check is used to ensure the current path is not a new path with a cycle
  * A global set is used to terminate a path that is known to lead to a cycle
* There are redirects to Philosophy (e.g. Philosophical) that should be valid. To handle these instances, the title of the page is checked to see if it says "Philosophy" even if the link that lead it to there may not be.
* On rare cases, the link may be to an internal Wikipedia domain (eg. Wikitionary). These are allowed.
* Sleep timer set to 0.3 seconds after each crawl
