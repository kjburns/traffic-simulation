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

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.github.kjburns.traffic_simulation.main.ProjectInputStreamProvider;
import com.github.kjburns.traffic_simulation.xml.ValidatingDocumentLoader;

public class ModelParametersImpl implements ModelParameters {
	private interface DistributionSetLoader {
		void loadDistributionSet(Element from);
	}
	
	private static final String TYPE_ATTR = "type";
	private static final String XSD_PATH = 
			"https://raw.githubusercontent.com/kjburns/traffic-simulation/develop/xml/distributions.xsd";
	private static final String DISTRIBUTION_SET_TAG = "distribution-set";
	private final Map<String, DistributionSetLoader> distributionSetLoaders = defineDistributionSetLoaders();
	
	/*
	 * Add distribution set instances here
	 */
	private ConnectorLinkSelectionBehaviorDistributionCollection connectorLinkSelectionBehaviors = null;
	private ConnectorMaxPositioningDistanceDistributionCollection connectorMaxPositioningDistances = null;

	public ModelParametersImpl(ProjectInputStreamProvider isProvider) throws ParserConfigurationException, SAXException, IOException {
		try(final InputStream distributionsStream = isProvider.createInputStreamForDistributions()) {
			Document doc = ValidatingDocumentLoader.loadDocument(distributionsStream, XSD_PATH);
			
			final Element docElement = doc.getDocumentElement();
			final NodeList elements = docElement.getElementsByTagName(DISTRIBUTION_SET_TAG);
			for (int i = 0; i < elements.getLength(); i++) {
				Element e = (Element)elements.item(i);
				String type = e.getAttribute(ModelParametersImpl.TYPE_ATTR);
				final DistributionSetLoader loader = distributionSetLoaders.get(type);
				if (loader != null) {
					loader.loadDistributionSet(e);
				} else {
					System.err.println("Error: Could not find loader for " + type);
				}
			}
		}
		
		testLatestFeature();
	}
	
	private void testLatestFeature() {
		connectorMaxPositioningDistances.stream().forEach((item) -> {
			System.out.println(item.getName());
		});
		final Distribution<Double> distr = connectorMaxPositioningDistances.getByUuid(
				UUID.fromString("1a48383c-800c-46ac-8828-43d4c373332f"));
		System.out.println(distr.getValue(0.47));
	}

	private Map<String, DistributionSetLoader> defineDistributionSetLoaders() {
		Map<String, DistributionSetLoader> ret = new HashMap<>();
		ret.put(ConnectorLinkSelectionBehaviorDistributionCollection.DISTRIBUTION_TYPE_VALUE, (from) -> {
			connectorLinkSelectionBehaviors = 
					new ConnectorLinkSelectionBehaviorDistributionCollection(from);
		});
		ret.put(ConnectorMaxPositioningDistanceDistributionCollection.DISTRIBUTION_TYPE_VALUE, (from) -> {
			connectorMaxPositioningDistances =
					new ConnectorMaxPositioningDistanceDistributionCollection(from);
		});
		
		/*
		 * Add new distribution set loaders above this comment
		 */

		return ret;
	}

	@Override
	public DistributionCollection<ConnectorLinkSelectionBehaviorEnum> getConnectorLinkSelectionBehaviors() {
		return connectorLinkSelectionBehaviors;
	}

	@Override
	public DistributionCollection<Double> getConnectorMaxPositioningDistances() {
		return connectorMaxPositioningDistances;
	}
}
