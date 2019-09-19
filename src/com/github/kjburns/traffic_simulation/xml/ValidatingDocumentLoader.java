/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.xml;

import java.io.IOException;
import java.io.InputStream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

/**
 * Loads an xml document and validates it against a schema.
 * <p>
 * If the document validates without errors or fatal errors, it is returned; otherwise,
 * a SAXException is raised detailing the validation problem.
 * </p>
 * @author Kevin J. Burns
 *
 */
public class ValidatingDocumentLoader {
	private static final ErrorHandler ERROR_HANDLER = new ErrorHandler() {
		@Override
		public void error(SAXParseException ex) throws SAXException {
			throw new SAXException(ex);
		}

		@Override
		public void fatalError(SAXParseException ex) throws SAXException {
			throw new SAXException(ex);
		}

		@Override
		public void warning(SAXParseException ex) throws SAXException {
		}
	};
	
	private static final String JAXP_SCHEMA_SOURCE = "http://java.sun.com/xml/jaxp/properties/schemaSource";
	private static final String JAXP_SCHEMA_LANGUAGE = "http://java.sun.com/xml/jaxp/properties/schemaLanguage";
	private static final String W3C_XML_SCHEMA = "http://www.w3.org/2001/XMLSchema";

	public static Document loadDocument(InputStream is, String xsdUrl) 
			throws ParserConfigurationException, SAXException, IOException {
		DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		dbf.setNamespaceAware(true);
		dbf.setValidating(true);
		dbf.setAttribute(JAXP_SCHEMA_LANGUAGE, W3C_XML_SCHEMA);
		dbf.setAttribute(JAXP_SCHEMA_SOURCE, xsdUrl);
		
		DocumentBuilder db = dbf.newDocumentBuilder();
		db.setErrorHandler(ERROR_HANDLER);
		return db.parse(is);
	}
}
