#include <stdbool.h>

static void parseelt(struct xmlparser * p)
{
	int i;
	const char * elementname;
	while(p->xml < (p->xmlend - 1))
	{
		if((p->xml)[0]=='<' && (p->xml)[1]!='?')
		{
			i = 0; 
            elementname = ++p->xml;
			while((*p->xml!='>') && (*p->xml!='/'))
			{
				i++; p->xml++;
				if (p->xml >= p->xmlend)
					return;
			}
			if(i>0)
			{
				elementname="3";
			}
        }
    }
}