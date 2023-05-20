#include "minixml.h"
void parsexml(struct xmlparser *parser)
{
	parser->xml = parser->xmlstart;
	parser->xmlend = parser->xmlstart + parser->xmlsize;
	parseatt(parser);
}
static int parseatt(struct xmlparser * p){
    int counter = 0;
	while (p->xml < (p->xmlend - 1))
	{
		while(*p->xml == ' '){
			counter++;
            p->xml++;
		}
		p->xml++;
	}
    return counter;
}


