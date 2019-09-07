package com.github.kjburns.traffic_simulation.parameters;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.io.InputStream;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.github.kjburns.traffic_simulation.parameters.NormalDistributionTruncatable.Factory;

class NormalDistributionTruncatableXmlTest {
	private final Distribution<Double> normalBell;
	private final Distribution<Double> reverseBell;
	private final Distribution<Double> truncatedBell;
	
	public NormalDistributionTruncatableXmlTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/NormalDistributionTruncatableTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("distr");
			normalBell = Factory.fromXml((Element)nodes.item(0));
			reverseBell = Factory.fromXml((Element)nodes.item(1));
			truncatedBell = Factory.fromXml((Element)nodes.item(2));
		}
	}
	
	@Test void testParameterLimits0() throws ParserConfigurationException, SAXException, IOException {
		assertThrows(RuntimeException.class, () -> {
			normalBell.getValue(-0.5);
		});
	}
	
	@Test void testParameterLimits1() {
		assertThrows(RuntimeException.class, () -> {
			normalBell.getValue(1.5);
		});
	}
	
	@Test void testUntruncatedResult0() {
		double expected = 3.0;
		double actual = normalBell.getValue(0.5);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testUntruncatedResult1() {
		double expected = -1.047;
		double actual = normalBell.getValue(0.25);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testReversedResult() {
		double expected = 7.047;
		double actual = reverseBell.getValue(0.25);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testTruncatedResult0() {
		double expected = 0.;
		double actual = truncatedBell.getValue(0.25);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testTruncatedResult1() {
		double expected = 7.047;
		double actual = truncatedBell.getValue(0.75);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testTruncatedResult2() {
		double expected = 10.;
		double actual = truncatedBell.getValue(0.9);
		assertEquals(expected, actual, 0.001);
	}
}
