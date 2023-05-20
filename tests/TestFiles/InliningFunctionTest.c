#include "minixml.h"
/* the parser must be initialized before calling this function */
void parsexml(struct xmlparser *parser)
{
	parser->xml = parser->xmlstart;
	parser->xmlend = parser->xmlstart + parser->xmlsize;
	parseatt(parser);
}
static int parseatt(struct xmlparser * p){
  int counter = 0;
  int i=0;
	while (p->xml < (p->xmlend - 1))
	{
		if (*p->xml == '/')
		{
			counter++;
		}
    i=0;
		while(i<counter){
			if((i%2)==0){
				counter--;
			}
      i++;
		}
		p->xml++;
	}
  return counter;
}
