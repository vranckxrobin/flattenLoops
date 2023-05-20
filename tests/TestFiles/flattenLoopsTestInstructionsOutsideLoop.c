#include <stdbool.h>

static void parseelt(struct xmlparser * p)
{
	int i;
	const char * elementname;
	while(p->xml < (p->xmlend - 1))
	{
		if((p->xml + 4) <= p->xmlend && (0 == memcmp(p->xml, "<!--", 4)))
		{
			p->xml += 3;
			p->xml += 4;
		}
		else if((p->xml)[0]=='<' && (p->xml)[1]!='?')
		{
			i = 0; 
            elementname = ++p->xml;
        }
    }
	elementname ="test";
}