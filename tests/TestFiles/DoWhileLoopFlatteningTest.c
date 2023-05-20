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
			do
			{
				p->xml++;
				if ((p->xml + 3) >= p->xmlend)
					return;
			}
			while (memcmp(p->xml, "-->", 3) != 0);
			p->xml += 1;
		}
    }
}