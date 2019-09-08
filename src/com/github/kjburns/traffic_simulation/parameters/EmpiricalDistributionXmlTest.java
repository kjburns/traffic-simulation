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
package com.github.kjburns.traffic_simulation.parameters;

import static org.junit.jupiter.api.Assertions.*;

import java.io.InputStream;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.github.kjburns.traffic_simulation.parameters.EmpiricalDistribution.Factory;

public class EmpiricalDistributionXmlTest {
	private final Distribution<Double> testCompleteDistribution;
	private final Distribution<Double> testIncompleteDisribution;

	public EmpiricalDistributionXmlTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/EmpiricalDistributionTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("distr");
			testCompleteDistribution = Factory.fromXml((Element)nodes.item(0));
			testIncompleteDisribution = Factory.fromXml((Element)nodes.item(1));
		}
	}

	@Test void testParameterLimits0() {
		assertThrows(RuntimeException.class, () -> {
			testCompleteDistribution.getValue(-0.5);
		});
	}
	
	@Test void testParameterLimits1() {
		assertThrows(RuntimeException.class, () -> {
			testCompleteDistribution.getValue(1.5);
		});
	}
	
	@Test void testValue0() {
		double expected = 11.5;
		double actual = testCompleteDistribution.getValue(0.15);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testValue1() {
		double expected = 15.6;
		double actual = testCompleteDistribution.getValue(0.56);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testValue2() {
		double expected = 20.0;
		double actual = testCompleteDistribution.getValue(1.0);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testIncompleteValue0() {
		double expected = 15.6;
		double actual = testIncompleteDisribution.getValue(0.56);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testIncompleteValue1() {
		double expected = 18.0;
		double actual = testIncompleteDisribution.getValue(0.95);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testIncompleteValue2() {
		double expected = 12.0;
		double actual = testIncompleteDisribution.getValue(0.15);
		assertEquals(expected, actual, 0.001);
	}
}
