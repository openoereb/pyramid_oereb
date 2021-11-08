<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ili="http://www.interlis.ch/INTERLIS2.3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:output omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/>
<xsl:template match="/">
[<xsl:for-each select="ili:TRANSFER/ili:DATASECTION/ili:OeREBKRMkvs_V2_0.Thema/ili:OeREBKRMkvs_V2_0.Thema.ThemaGesetz">
    {
        "theme_id": "<xsl:value-of select="ili:Thema/@REF"/>",
        "document_id": "<xsl:value-of select="ili:Gesetz/@REF"/>",
        "article_numbers": <xsl:choose><xsl:when test="count(ili:ArtikelNr) &gt; 0">[<xsl:for-each select="ili:ArtikelNr/ili:OeREBKRM_V2_0.ArtikelNummer_">"<xsl:value-of select="ili:value"/>"<xsl:if test="not(position() = last())">,</xsl:if></xsl:for-each>]</xsl:when><xsl:otherwise> null</xsl:otherwise></xsl:choose>
    }<xsl:if test="not(position() = last())">,</xsl:if>
</xsl:for-each>
]
</xsl:template>
</xsl:stylesheet>
