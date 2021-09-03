<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:output omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/>
<xsl:template match="/">
[
<xsl:for-each select="TRANSFER/DATASECTION/OeREBKRMkvs_V2_0.Thema[@BID='ch.admin.v_d.oerebkrmkvs_thema']/OeREBKRMkvs_V2_0.Thema.Thema[@TID='ch.Nutzungsplanung']">
code: <xsl:value-of select="OeREBKRMkvs_V2_0.Thema.Thema/Code"/>
</xsl:for-each>
]
</xsl:template>
</xsl:stylesheet>
